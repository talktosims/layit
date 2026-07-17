import SwiftUI
import WebKit
import Vision
import UIKit
import StoreKit

struct WebAppView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()

        // Use default data store so localStorage persists between app launches
        config.websiteDataStore = WKWebsiteDataStore.default()

        // Allow inline media playback (needed for camera/barcode scanning)
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []

        // Register purchase message handler
        let coordinator = context.coordinator
        config.userContentController.add(coordinator, name: "purchase")
        config.userContentController.add(coordinator, name: "restorePurchases")
        config.userContentController.add(coordinator, name: "manageSubscriptions")
        config.userContentController.add(coordinator, name: "shareHtml")
        config.userContentController.add(coordinator, name: "scanBarcode")
        config.userContentController.add(coordinator, name: "scanLabelOCR")
        config.userContentController.add(coordinator, name: "detectBarcodeInImage")
        config.userContentController.add(coordinator, name: "openURL")
        #if DEBUG
        config.userContentController.add(coordinator, name: "setDevProOverride")
        #endif

        let webView = WKWebView(frame: .zero, configuration: config)

        // Set delegate to handle camera permission prompts
        webView.uiDelegate = coordinator
        webView.navigationDelegate = coordinator

        // Dark background matching the app theme (#080b12)
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.031, green: 0.043, blue: 0.071, alpha: 1.0)
        webView.scrollView.backgroundColor = UIColor(red: 0.031, green: 0.043, blue: 0.071, alpha: 1.0)

        // Disable bouncing for a native feel
        webView.scrollView.bounces = false
        webView.scrollView.alwaysBounceVertical = false
        webView.scrollView.alwaysBounceHorizontal = false

        // Disable content inset adjustments so web content fills the full screen
        webView.scrollView.contentInsetAdjustmentBehavior = .never

        // Disable back/forward navigation gestures
        webView.allowsBackForwardNavigationGestures = false

        // Warm up StoreKit state before the web app asks about Pro access.
        _ = StoreManager.shared

        // Start local server and load through localhost (required for getUserMedia camera access)
        coordinator.webView = webView
        coordinator.startServer()
        if let port = coordinator.serverPort {
            let cacheBust = Int(Date().timeIntervalSince1970)
            var components = URLComponents(string: "http://localhost:\(port)/index.html")!
            components.queryItems = [
                URLQueryItem(name: "v", value: String(cacheBust))
            ]
            let url = components.url!
            var request = URLRequest(url: url)
            request.cachePolicy = .reloadIgnoringLocalCacheData
            webView.load(request)
        }

        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        // No dynamic updates needed
    }

    class Coordinator: NSObject, WKUIDelegate, WKNavigationDelegate, WKScriptMessageHandler {
        private static let preferredPorts: [UInt16] = [8787, 8788, 8789, 8790]
        var serverPort: UInt16?
        weak var webView: WKWebView?
        private var listenSocket: Int32 = -1
        private var serverThread: Thread?
        private var webAppPath: String = ""
        private var didBecomeActiveObserver: NSObjectProtocol?
        #if DEBUG
        private var didPresentReviewPaywall = false
        #endif

        override init() {
            super.init()
            didBecomeActiveObserver = NotificationCenter.default.addObserver(
                forName: UIApplication.didBecomeActiveNotification,
                object: nil,
                queue: .main
            ) { [weak self] _ in
                self?.refreshAndInjectProStatus()
            }
        }

        func startServer() {
            guard let webAppURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "WebApp") else { return }
            webAppPath = webAppURL.deletingLastPathComponent().path

            // Create socket
            listenSocket = socket(AF_INET, SOCK_STREAM, 0)
            guard listenSocket >= 0 else { return }

            var reuse: Int32 = 1
            setsockopt(listenSocket, SOL_SOCKET, SO_REUSEADDR, &reuse, socklen_t(MemoryLayout<Int32>.size))

            var bound = false
            for preferredPort in Self.preferredPorts {
                var addr = sockaddr_in()
                addr.sin_family = sa_family_t(AF_INET)
                addr.sin_addr.s_addr = inet_addr("127.0.0.1")
                addr.sin_port = preferredPort.bigEndian

                let bindResult = withUnsafePointer(to: &addr) {
                    $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                        bind(listenSocket, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
                    }
                }
                if bindResult == 0 {
                    serverPort = preferredPort
                    bound = true
                    break
                }
            }
            guard bound, serverPort != nil else { Darwin.close(listenSocket); return }

            listen(listenSocket, 10)

            // Accept connections on background thread
            let sock = listenSocket
            let path = webAppPath
            serverThread = Thread {
                while true {
                    let client = accept(sock, nil, nil)
                    if client < 0 { break }
                    Self.handleClient(client, webAppPath: path)
                }
            }
            serverThread?.start()
        }

        private static func handleClient(_ client: Int32, webAppPath: String) {
            // Read request
            var buffer = [UInt8](repeating: 0, count: 8192)
            let bytesRead = recv(client, &buffer, buffer.count, 0)
            guard bytesRead > 0 else { Darwin.close(client); return }

            let request = String(bytes: buffer[0..<bytesRead], encoding: .utf8) ?? ""
            let lines = request.components(separatedBy: "\r\n")
            guard let firstLine = lines.first else { Darwin.close(client); return }
            let parts = firstLine.components(separatedBy: " ")
            guard parts.count >= 2 else { Darwin.close(client); return }
            guard parts[0] == "GET" || parts[0] == "HEAD" else {
                let resp = "HTTP/1.1 405 Method Not Allowed\r\nContent-Length: 0\r\n\r\n"
                Self.sendAll(client, data: Data(resp.utf8))
                Darwin.close(client)
                return
            }

            var requestedPath = parts[1]
            if requestedPath == "/" { requestedPath = "/index.html" }
            if let q = requestedPath.firstIndex(of: "?") { requestedPath = String(requestedPath[..<q]) }
            requestedPath = requestedPath.removingPercentEncoding ?? requestedPath

            let relativePath = requestedPath.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
            guard !relativePath.isEmpty,
                  !relativePath.split(separator: "/").contains("..") else {
                let resp = "HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"
                Self.sendAll(client, data: Data(resp.utf8))
                Darwin.close(client)
                return
            }

            let rootURL = URL(fileURLWithPath: webAppPath, isDirectory: true).standardizedFileURL
            let fileURL = rootURL.appendingPathComponent(relativePath).standardizedFileURL
            guard fileURL.path.hasPrefix(rootURL.path + "/"),
                  FileManager.default.fileExists(atPath: fileURL.path),
                  let data = try? Data(contentsOf: fileURL) else {
                let resp = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
                Self.sendAll(client, data: Data(resp.utf8))
                Darwin.close(client)
                return
            }

            let ext = fileURL.pathExtension.lowercased()
            let mime: String
            switch ext {
            case "html": mime = "text/html"
            case "js": mime = "application/javascript"
            case "css": mime = "text/css"
            case "json": mime = "application/json"
            case "png": mime = "image/png"
            case "jpg", "jpeg": mime = "image/jpeg"
            case "svg": mime = "image/svg+xml"
            case "woff2": mime = "font/woff2"
            default: mime = "application/octet-stream"
            }

            let header = "HTTP/1.1 200 OK\r\nContent-Type: \(mime)\r\nContent-Length: \(data.count)\r\nCache-Control: no-store, no-cache, must-revalidate, max-age=0\r\nPragma: no-cache\r\nExpires: 0\r\nX-Content-Type-Options: nosniff\r\n\r\n"
            Self.sendAll(client, data: Data(header.utf8))
            if parts[0] == "GET" {
                Self.sendAll(client, data: data)
            }
            Darwin.close(client)
        }

        private static func sendAll(_ socket: Int32, data: Data) {
            data.withUnsafeBytes { rawBuffer in
                guard let baseAddress = rawBuffer.baseAddress else { return }
                var totalSent = 0
                while totalSent < data.count {
                    let sent = Darwin.send(
                        socket,
                        baseAddress.advanced(by: totalSent),
                        data.count - totalSent,
                        0
                    )
                    if sent <= 0 { break }
                    totalSent += sent
                }
            }
        }

        // Grant camera only to LayIt's exact loopback origin. Microphone is never required.
        func webView(_ webView: WKWebView,
                     requestMediaCapturePermissionFor origin: WKSecurityOrigin,
                     initiatedByFrame frame: WKFrameInfo,
                     type: WKMediaCaptureType,
                     decisionHandler: @escaping (WKPermissionDecision) -> Void) {
            let isLayItOrigin = origin.protocol == "http"
                && origin.host == "localhost"
                && origin.port == Int(serverPort ?? 0)
            decisionHandler(isLayItOrigin && type == .camera ? .grant : .deny)
        }

        // MARK: - Navigation Delegate — Inject Pro Status

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            refreshAndInjectProStatus()
            presentReviewPaywallIfRequested(in: webView)
        }

        #if DEBUG
        /// Debug-only launch aid used to capture App Review evidence without
        /// adding a hidden route or test behavior to the shipping build.
        private func presentReviewPaywallIfRequested(in webView: WKWebView) {
            guard !didPresentReviewPaywall,
                  ProcessInfo.processInfo.environment["LAYIT_REVIEW_MODE"] == "paywall" else { return }
            didPresentReviewPaywall = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                let js = """
                if (typeof completeOnboarding === 'function') { completeOnboarding(); }
                if (typeof showUpgradeModal === 'function') { showUpgradeModal(); }
                """
                webView.evaluateJavaScript(js)
            }
        }
        #else
        private func presentReviewPaywallIfRequested(in webView: WKWebView) {}
        #endif

        func webView(_ webView: WKWebView,
                     decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.cancel)
                return
            }

            if url.scheme == "http",
               url.host == "localhost",
               url.port == Int(serverPort ?? 0) {
                decisionHandler(.allow)
                return
            }

            if Self.isAllowedExternalURL(url) {
                UIApplication.shared.open(url)
            }
            decisionHandler(.cancel)
        }

        private static func isAllowedExternalURL(_ url: URL) -> Bool {
            guard url.scheme == "https", let host = url.host?.lowercased() else { return false }
            return ["layit.pages.dev", "apps.apple.com", "www.google.com", "google.com"].contains(host)
        }

        // Safe-by-default launch configuration:
        // - No embedded AI API key in the app binary
        // - Optional proxy URL can be provided in Info.plist via LayItAIProxyURL
        private let aiApiKey = ""
        private var aiProxyURL: String {
            (Bundle.main.object(forInfoDictionaryKey: "LayItAIProxyURL") as? String) ?? ""
        }
        private var aiProxyProfile: String {
            (Bundle.main.object(forInfoDictionaryKey: "LayItAIProxyProfile") as? String) ?? ""
        }
        private var aiTextModel: String {
            (Bundle.main.object(forInfoDictionaryKey: "LayItAITextModel") as? String) ?? ""
        }
        private var aiVisionModel: String {
            (Bundle.main.object(forInfoDictionaryKey: "LayItAIVisionModel") as? String) ?? ""
        }
        private var isDebugBuild: Bool {
            #if DEBUG
            true
            #else
            false
            #endif
        }
        private var isDevProOverrideEnabled: Bool {
            #if DEBUG
            UserDefaults.standard.bool(forKey: "layit_dev_pro_override")
            #else
            false
            #endif
        }

        func injectProStatus() {
            let isPro = StoreManager.shared.isPro || isDevProOverrideEnabled
            let productPayload = StoreManager.shared.webProductPayload()
            let productJSON: String
            if let data = try? JSONSerialization.data(withJSONObject: productPayload),
               let json = String(data: data, encoding: .utf8) {
                productJSON = json
            } else {
                productJSON = "[]"
            }
            let js = """
            window._nativeApp = true;
            window._layitDebugBuild = \(isDebugBuild ? "true" : "false");
            proUser = \(isPro ? "true" : "false");
            localStorage.setItem('layit_pro', '\(isPro ? "true" : "false")');
            localStorage.setItem('layit_ai_key', '\(aiApiKey)');
            localStorage.setItem('layit_ai_proxy_url', '\(aiProxyURL)');
            localStorage.setItem('layit_ai_proxy_profile', '\(aiProxyProfile)');
            localStorage.setItem('layit_ai_text_model', '\(aiTextModel)');
            localStorage.setItem('layit_ai_vision_model', '\(aiVisionModel)');
            _AI_API_KEY = localStorage.getItem('layit_ai_key') || '';
            _AI_PROXY_URL = localStorage.getItem('layit_ai_proxy_url') || '';
            _AI_PROXY_PROFILE = localStorage.getItem('layit_ai_proxy_profile') || '';
            _AI_TEXT_MODEL = localStorage.getItem('layit_ai_text_model') || '';
            _AI_VISION_MODEL = localStorage.getItem('layit_ai_vision_model') || '';
            if (typeof setSubscriptionProducts === 'function') { setSubscriptionProducts(\(productJSON)); }
            if (typeof updateProUI === 'function') { updateProUI(); }
            """
            Task { @MainActor in
                try? await webView?.evaluateJavaScript(js)
            }
        }

        func refreshAndInjectProStatus() {
            injectProStatus()
            Task { @MainActor [weak self] in
                await StoreManager.shared.loadProducts()
                await StoreManager.shared.refreshEntitlements()
                self?.injectProStatus()
            }
        }

        // MARK: - WKScriptMessageHandler — Purchase Bridge

        func userContentController(_ userContentController: WKUserContentController,
                                   didReceive message: WKScriptMessage) {
            if message.name == "purchase" {
                guard let plan = message.body as? String else { return }
                let productID: String
                switch plan {
                case "monthly":
                    productID = StoreManager.monthlyID
                case "annual":
                    productID = StoreManager.annualID
                default:
                    print("[WebAppView] Unknown purchase plan: \(plan)")
                    return
                }

                Task { @MainActor in
                    let success = await StoreManager.shared.purchase(productID)
                    if success {
                        let js = """
                        proUser = true;
                        localStorage.setItem('layit_pro', 'true');
                        closeUpgradeModal();
                        updateProUI();
                        launchConfetti();
                        showToast('\\u2713 LayIt Pro activated!', 2000);
                        """
                        _ = try? await self.webView?.evaluateJavaScript(js)
                    } else {
                        let js = "showToast('Purchase was not completed', 2000);"
                        _ = try? await self.webView?.evaluateJavaScript(js)
                    }
                }
            } else if message.name == "restorePurchases" {
                Task { @MainActor in
                    await StoreManager.shared.restorePurchases()
                    self.injectProStatus()
                    let isPro = StoreManager.shared.isPro
                    let msg = isPro ? "\\u2713 Purchases restored!" : "No active subscriptions found"
                    let js = "showToast('\(msg)', 2000);"
                    _ = try? await self.webView?.evaluateJavaScript(js)
                }
            } else if message.name == "manageSubscriptions" {
                Task { @MainActor in
                    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene else { return }
                    do {
                        try await AppStore.showManageSubscriptions(in: scene)
                    } catch {
                        let js = "showToast('Unable to open subscription management', 2500);"
                        _ = try? await self.webView?.evaluateJavaScript(js)
                    }
                }
            } else if message.name == "setDevProOverride" {
                #if DEBUG
                let enabled: Bool
                if let boolValue = message.body as? Bool {
                    enabled = boolValue
                } else if let stringValue = message.body as? String {
                    enabled = NSString(string: stringValue).boolValue
                } else {
                    enabled = false
                }
                UserDefaults.standard.set(enabled, forKey: "layit_dev_pro_override")
                injectProStatus()
                #endif
            } else if message.name == "scanBarcode" {
                Task { @MainActor in
                    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                          let rootVC = scene.windows.first?.rootViewController else { return }

                    let scanner = BarcodeScannerController()
                    scanner.modalPresentationStyle = .fullScreen

                    scanner.onBarcode = { [weak self] barcode in
                        // Pass barcode as JSON string so quotes / odd Code128 chars cannot break JS
                        guard let data = try? JSONEncoder().encode(barcode),
                              let jsonLiteral = String(data: data, encoding: .utf8) else { return }
                        let js = "onBarcodeDetected(\(jsonLiteral));"
                        Task { @MainActor in
                            _ = try? await self?.webView?.evaluateJavaScript(js)
                        }
                    }

                    scanner.onCancel = { [weak self] in
                        let js = "closeBarcodeScanner();"
                        Task { @MainActor in
                            _ = try? await self?.webView?.evaluateJavaScript(js)
                        }
                    }

                    rootVC.present(scanner, animated: true)
                }
            } else if message.name == "scanLabelOCR" {
                Task { @MainActor in
                    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                          let rootVC = scene.windows.first?.rootViewController else { return }

                    let scanner = LabelScannerController()
                    scanner.modalPresentationStyle = .fullScreen

                    scanner.onResult = { [weak self] payload in
                        guard let data = try? JSONEncoder().encode(payload),
                              let jsonLiteral = String(data: data, encoding: .utf8) else { return }
                        let js = "onLabelScanResult(\(jsonLiteral));"
                        Task { @MainActor in
                            _ = try? await self?.webView?.evaluateJavaScript(js)
                        }
                    }

                    scanner.onCancel = { [weak self] in
                        let js = "closeTileScanInstructionModal();"
                        Task { @MainActor in
                            _ = try? await self?.webView?.evaluateJavaScript(js)
                        }
                    }

                    rootVC.present(scanner, animated: true)
                }
            } else if message.name == "detectBarcodeInImage" {
                guard let body = message.body as? [String: Any],
                      let requestId = body["requestId"] as? String,
                      let imageBase64 = body["imageBase64"] as? String,
                      let imageData = Data(base64Encoded: imageBase64),
                      let uiImage = UIImage(data: imageData),
                      let cgImage = uiImage.cgImage else {
                    let js = "onNativeBarcodeDetectionResult(null, null);"
                    Task { @MainActor in
                        _ = try? await self.webView?.evaluateJavaScript(js)
                    }
                    return
                }

                DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                    let request = VNDetectBarcodesRequest()
                    request.symbologies = [.ean13, .ean8, .upce, .code128, .code39, .code93, .i2of5]
                    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
                    var detectedBarcode: String? = nil
                    do {
                        try handler.perform([request])
                        let observations = request.results ?? []
                        detectedBarcode = observations
                            .compactMap { $0.payloadStringValue?.trimmingCharacters(in: .whitespacesAndNewlines) }
                            .first(where: { !$0.isEmpty })
                    } catch {
                        print("LayIt native barcode detect error: \(error.localizedDescription)")
                    }

                    Task { @MainActor in
                        guard let self = self,
                              let reqData = try? JSONEncoder().encode(requestId),
                              let reqLiteral = String(data: reqData, encoding: .utf8) else { return }
                        let resultLiteral: String
                        if let detectedBarcode,
                           let barcodeData = try? JSONEncoder().encode(detectedBarcode),
                           let barcodeLiteral = String(data: barcodeData, encoding: .utf8) {
                            resultLiteral = barcodeLiteral
                        } else {
                            resultLiteral = "null"
                        }
                        let js = "onNativeBarcodeDetectionResult(\(reqLiteral), \(resultLiteral));"
                        _ = try? await self.webView?.evaluateJavaScript(js)
                    }
                }
            } else if message.name == "openURL" {
                guard let urlString = message.body as? String,
                      let url = URL(string: urlString),
                      Self.isAllowedExternalURL(url) else { return }
                Task { @MainActor in
                    UIApplication.shared.open(url)
                }
            } else if message.name == "shareHtml" {
                guard let htmlString = message.body as? String else { return }
                Task { @MainActor in
                    // Save HTML to temp file
                    let tempDir = FileManager.default.temporaryDirectory
                    let fileURL = tempDir.appendingPathComponent("TileLayout.html")
                    try? htmlString.write(to: fileURL, atomically: true, encoding: .utf8)

                    // Present share sheet
                    let activityVC = UIActivityViewController(
                        activityItems: [fileURL],
                        applicationActivities: nil
                    )

                    if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                       let rootVC = scene.windows.first?.rootViewController {
                        rootVC.present(activityVC, animated: true)
                    }
                }
            }
        }

        deinit {
            if let didBecomeActiveObserver {
                NotificationCenter.default.removeObserver(didBecomeActiveObserver)
            }
            if listenSocket >= 0 { Darwin.close(listenSocket) }
        }
    }
}
