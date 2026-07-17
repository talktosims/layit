import SwiftUI
import AVFoundation
import Vision

/// Native AVFoundation barcode scanner presented as a full-screen overlay.
/// User captures a photo, then barcode is detected from the still image.
/// Returns scanned barcode string via completion handler.

class BarcodeScannerController: UIViewController, AVCapturePhotoCaptureDelegate {
    var onBarcode: ((String) -> Void)?
    var onCancel: (() -> Void)?

    private var captureSession: AVCaptureSession?
    private var previewLayer: AVCaptureVideoPreviewLayer?
    private var videoDevice: AVCaptureDevice?
    private let photoOutput = AVCapturePhotoOutput()
    private var isCapturingPhoto = false
    private weak var statusLabel: UILabel?
    private weak var captureButton: UIButton?

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black
        setupCamera()
        setupUI()
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(subjectAreaDidChange),
            name: AVCaptureDevice.subjectAreaDidChangeNotification,
            object: videoDevice
        )
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        previewLayer?.frame = view.bounds
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        captureSession?.stopRunning()
    }

    override var prefersStatusBarHidden: Bool { true }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }

    private func setupCamera() {
        let session = AVCaptureSession()
        session.sessionPreset = .high

        guard let device = AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device) else {
            showError("Camera not available")
            return
        }
        videoDevice = device
        configureAutoFocus(device)

        if session.canAddInput(input) {
            session.addInput(input)
        }

        if session.canAddOutput(photoOutput) {
            session.addOutput(photoOutput)
            if let maxDimensions = device.activeFormat.supportedMaxPhotoDimensions.max(by: {
                Int64($0.width) * Int64($0.height) < Int64($1.width) * Int64($1.height)
            }) {
                photoOutput.maxPhotoDimensions = maxDimensions
            }
        }

        let preview = AVCaptureVideoPreviewLayer(session: session)
        preview.videoGravity = .resizeAspectFill
        preview.frame = view.bounds
        view.layer.addSublayer(preview)

        captureSession = session
        previewLayer = preview
    }

    private func configureAutoFocus(_ device: AVCaptureDevice) {
        do {
            try device.lockForConfiguration()
            // Keep focus hunting continuously so web/monitor barcodes can resolve sharply.
            if device.isFocusModeSupported(.continuousAutoFocus) {
                device.focusMode = .continuousAutoFocus
            } else if device.isFocusModeSupported(.autoFocus) {
                device.focusMode = .autoFocus
            }
            if device.isSmoothAutoFocusSupported {
                device.isSmoothAutoFocusEnabled = true
            }
            if device.isExposureModeSupported(.continuousAutoExposure) {
                device.exposureMode = .continuousAutoExposure
            }
            if device.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
                device.whiteBalanceMode = .continuousAutoWhiteBalance
            }
            device.isSubjectAreaChangeMonitoringEnabled = true
            device.unlockForConfiguration()
        } catch {
            // Fall back to default camera behavior if locking fails.
            print("LayIt scanner autofocus config failed: \(error.localizedDescription)")
        }
    }

    private func setupUI() {
        let label = UILabel()
        label.text = "Center barcode in camera, then tap Capture"
        label.textColor = .white
        label.font = .systemFont(ofSize: 16, weight: .semibold)
        label.textAlignment = .center
        label.numberOfLines = 2
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            label.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            label.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20)
        ])
        statusLabel = label

        let captureBtn = UIButton(type: .system)
        captureBtn.setTitle("Capture", for: .normal)
        captureBtn.titleLabel?.font = .systemFont(ofSize: 18, weight: .bold)
        captureBtn.setTitleColor(.white, for: .normal)
        captureBtn.backgroundColor = UIColor(red: 0.15, green: 0.72, blue: 0.34, alpha: 0.95)
        captureBtn.layer.cornerRadius = 28
        captureBtn.translatesAutoresizingMaskIntoConstraints = false
        captureBtn.addTarget(self, action: #selector(captureTapped), for: .touchUpInside)
        view.addSubview(captureBtn)
        NSLayoutConstraint.activate([
            captureBtn.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            captureBtn.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -94),
            captureBtn.widthAnchor.constraint(equalToConstant: 180),
            captureBtn.heightAnchor.constraint(equalToConstant: 56)
        ])
        captureButton = captureBtn

        // Cancel button
        let cancelBtn = UIButton(type: .system)
        cancelBtn.setTitle("Cancel", for: .normal)
        cancelBtn.titleLabel?.font = .systemFont(ofSize: 17, weight: .semibold)
        cancelBtn.setTitleColor(.white, for: .normal)
        cancelBtn.backgroundColor = UIColor(white: 0.2, alpha: 0.8)
        cancelBtn.layer.cornerRadius = 22
        cancelBtn.translatesAutoresizingMaskIntoConstraints = false
        cancelBtn.addTarget(self, action: #selector(cancelTapped), for: .touchUpInside)
        view.addSubview(cancelBtn)
        NSLayoutConstraint.activate([
            cancelBtn.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            cancelBtn.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -26),
            cancelBtn.widthAnchor.constraint(equalToConstant: 140),
            cancelBtn.heightAnchor.constraint(equalToConstant: 44)
        ])
    }

    @objc private func subjectAreaDidChange() {
        guard let device = videoDevice else { return }
        do {
            try device.lockForConfiguration()
            if device.isFocusPointOfInterestSupported {
                device.focusPointOfInterest = CGPoint(x: 0.5, y: 0.5)
            }
            if device.isFocusModeSupported(.continuousAutoFocus) {
                device.focusMode = .continuousAutoFocus
            }
            if device.isExposurePointOfInterestSupported {
                device.exposurePointOfInterest = CGPoint(x: 0.5, y: 0.5)
            }
            if device.isExposureModeSupported(.continuousAutoExposure) {
                device.exposureMode = .continuousAutoExposure
            }
            device.unlockForConfiguration()
        } catch {
            print("LayIt scanner refocus failed: \(error.localizedDescription)")
        }
    }

    private func showError(_ msg: String) {
        let label = UILabel()
        label.text = msg
        label.textColor = .white
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func cancelTapped() {
        captureSession?.stopRunning()
        onCancel?()
        dismiss(animated: true)
    }

    @objc private func captureTapped() {
        guard !isCapturingPhoto else { return }
        isCapturingPhoto = true
        captureButton?.isEnabled = false
        statusLabel?.text = "Reading barcode..."

        let settings = AVCapturePhotoSettings()
        settings.flashMode = .off
        photoOutput.capturePhoto(with: settings, delegate: self)
    }

    // MARK: - AVCapturePhotoCaptureDelegate

    func photoOutput(_ output: AVCapturePhotoOutput,
                     didFinishProcessingPhoto photo: AVCapturePhoto,
                     error: Error?) {
        if let error = error {
            statusLabel?.text = "Capture failed. Try again."
            captureButton?.isEnabled = true
            isCapturingPhoto = false
            print("LayIt scanner photo capture error: \(error.localizedDescription)")
            return
        }
        guard let cgImage = photo.cgImageRepresentation() else {
            statusLabel?.text = "Could not read photo. Try again."
            captureButton?.isEnabled = true
            isCapturingPhoto = false
            return
        }

        let request = VNDetectBarcodesRequest()
        request.symbologies = [.ean13, .ean8, .upce, .code128, .code39, .code93, .i2of5]

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([request])
                let observations = request.results ?? []
                let value = observations.compactMap { $0.payloadStringValue?.trimmingCharacters(in: .whitespacesAndNewlines) }
                    .first(where: { !$0.isEmpty })
                DispatchQueue.main.async {
                    if let barcode = value {
                        self.handleDetectedBarcode(barcode)
                    } else {
                        self.statusLabel?.text = "No barcode found. Reframe and capture again."
                        self.captureButton?.isEnabled = true
                        self.isCapturingPhoto = false
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusLabel?.text = "Read failed. Try again."
                    self.captureButton?.isEnabled = true
                    self.isCapturingPhoto = false
                }
                print("LayIt scanner Vision decode error: \(error.localizedDescription)")
            }
        }
    }

    private func handleDetectedBarcode(_ barcode: String) {
        captureSession?.stopRunning()
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)

        let flash = UIView(frame: view.bounds)
        flash.backgroundColor = UIColor(red: 0.3, green: 0.85, blue: 0.4, alpha: 0.35)
        view.addSubview(flash)
        UIView.animate(withDuration: 0.25, animations: { flash.alpha = 0 }) { _ in
            flash.removeFromSuperview()
        }

        statusLabel?.text = "Barcode found"
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) { [weak self] in
            self?.onBarcode?(barcode)
            self?.dismiss(animated: true)
        }
    }
}

struct LabelScanPayload: Codable {
    let text: String
    let barcode: String?
    let imageBase64: String?
}

final class LabelScannerController: UIViewController, AVCapturePhotoCaptureDelegate {
    var onResult: ((LabelScanPayload) -> Void)?
    var onCancel: (() -> Void)?

    private var captureSession: AVCaptureSession?
    private var previewLayer: AVCaptureVideoPreviewLayer?
    private var videoDevice: AVCaptureDevice?
    private let photoOutput = AVCapturePhotoOutput()
    private var isCapturingPhoto = false
    private weak var statusLabel: UILabel?
    private weak var captureButton: UIButton?
    private weak var focusIndicatorView: UIView?

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black
        setupCamera()
        setupUI()
        setupGestures()
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(subjectAreaDidChange),
            name: AVCaptureDevice.subjectAreaDidChangeNotification,
            object: videoDevice
        )
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        previewLayer?.frame = view.bounds
        updatePreviewOrientation()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        captureSession?.stopRunning()
    }

    override var prefersStatusBarHidden: Bool { true }
    override var shouldAutorotate: Bool { false }
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { .portrait }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }

    private func setupCamera() {
        let session = AVCaptureSession()
        session.sessionPreset = .high

        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) ?? AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device) else {
            showError("Camera not available")
            return
        }
        videoDevice = device
        configureAutoFocus(device)

        if session.canAddInput(input) {
            session.addInput(input)
        }

        if session.canAddOutput(photoOutput) {
            session.addOutput(photoOutput)
            if let maxDimensions = device.activeFormat.supportedMaxPhotoDimensions.max(by: {
                Int64($0.width) * Int64($0.height) < Int64($1.width) * Int64($1.height)
            }) {
                photoOutput.maxPhotoDimensions = maxDimensions
            }
        }

        let preview = AVCaptureVideoPreviewLayer(session: session)
        preview.videoGravity = .resizeAspectFill
        preview.frame = view.bounds
        view.layer.addSublayer(preview)

        captureSession = session
        previewLayer = preview
    }

    private func updatePreviewOrientation() {
        guard let connection = previewLayer?.connection, connection.isVideoOrientationSupported else { return }
        connection.videoOrientation = .portrait
    }

    private func configureAutoFocus(_ device: AVCaptureDevice) {
        do {
            try device.lockForConfiguration()
            if device.isFocusModeSupported(.continuousAutoFocus) {
                device.focusMode = .continuousAutoFocus
            } else if device.isFocusModeSupported(.autoFocus) {
                device.focusMode = .autoFocus
            }
            if device.isSmoothAutoFocusSupported {
                device.isSmoothAutoFocusEnabled = true
            }
            if device.isAutoFocusRangeRestrictionSupported {
                device.autoFocusRangeRestriction = .near
            }
            if device.isExposureModeSupported(.continuousAutoExposure) {
                device.exposureMode = .continuousAutoExposure
            }
            if device.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
                device.whiteBalanceMode = .continuousAutoWhiteBalance
            }
            device.isSubjectAreaChangeMonitoringEnabled = true
            device.unlockForConfiguration()
        } catch {
            print("LayIt label OCR autofocus config failed: \(error.localizedDescription)")
        }
    }

    private func setupUI() {
        let label = UILabel()
        label.text = "Capture the tile box label"
        label.textColor = .white
        label.font = .systemFont(ofSize: 16, weight: .semibold)
        label.textAlignment = .center
        label.numberOfLines = 2
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            label.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            label.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20)
        ])
        statusLabel = label

        let captureBtn = UIButton(type: .system)
        captureBtn.setTitle("Capture Label", for: .normal)
        captureBtn.titleLabel?.font = .systemFont(ofSize: 18, weight: .bold)
        captureBtn.setTitleColor(.white, for: .normal)
        captureBtn.backgroundColor = UIColor(red: 0.15, green: 0.72, blue: 0.34, alpha: 0.95)
        captureBtn.layer.cornerRadius = 28
        captureBtn.translatesAutoresizingMaskIntoConstraints = false
        captureBtn.addTarget(self, action: #selector(captureTapped), for: .touchUpInside)
        view.addSubview(captureBtn)
        NSLayoutConstraint.activate([
            captureBtn.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            captureBtn.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -94),
            captureBtn.widthAnchor.constraint(equalToConstant: 180),
            captureBtn.heightAnchor.constraint(equalToConstant: 56)
        ])
        captureButton = captureBtn

        let cancelBtn = UIButton(type: .system)
        cancelBtn.setTitle("Cancel", for: .normal)
        cancelBtn.titleLabel?.font = .systemFont(ofSize: 17, weight: .semibold)
        cancelBtn.setTitleColor(.white, for: .normal)
        cancelBtn.backgroundColor = UIColor(white: 0.2, alpha: 0.8)
        cancelBtn.layer.cornerRadius = 22
        cancelBtn.translatesAutoresizingMaskIntoConstraints = false
        cancelBtn.addTarget(self, action: #selector(cancelTapped), for: .touchUpInside)
        view.addSubview(cancelBtn)
        NSLayoutConstraint.activate([
            cancelBtn.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            cancelBtn.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -26),
            cancelBtn.widthAnchor.constraint(equalToConstant: 140),
            cancelBtn.heightAnchor.constraint(equalToConstant: 44)
        ])

        let focusIndicator = UIView()
        focusIndicator.translatesAutoresizingMaskIntoConstraints = true
        focusIndicator.frame = CGRect(x: 0, y: 0, width: 96, height: 96)
        focusIndicator.layer.borderWidth = 2
        focusIndicator.layer.borderColor = UIColor.systemYellow.cgColor
        focusIndicator.layer.cornerRadius = 16
        focusIndicator.alpha = 0
        focusIndicator.isUserInteractionEnabled = false
        view.addSubview(focusIndicator)
        focusIndicatorView = focusIndicator
    }

    private func setupGestures() {
        let tap = UITapGestureRecognizer(target: self, action: #selector(handlePreviewTap(_:)))
        view.addGestureRecognizer(tap)
    }

    @objc private func handlePreviewTap(_ gesture: UITapGestureRecognizer) {
        let point = gesture.location(in: view)
        focusCamera(at: point, userInitiated: true)
    }

    private func focusCamera(at viewPoint: CGPoint, userInitiated: Bool) {
        guard let device = videoDevice, let previewLayer = previewLayer else { return }
        let devicePoint = previewLayer.captureDevicePointConverted(fromLayerPoint: viewPoint)
        do {
            try device.lockForConfiguration()
            if device.isFocusPointOfInterestSupported {
                device.focusPointOfInterest = devicePoint
            }
            if userInitiated, device.isFocusModeSupported(.autoFocus) {
                device.focusMode = .autoFocus
            } else if device.isFocusModeSupported(.continuousAutoFocus) {
                device.focusMode = .continuousAutoFocus
            }
            if device.isExposurePointOfInterestSupported {
                device.exposurePointOfInterest = devicePoint
            }
            if device.isExposureModeSupported(.continuousAutoExposure) {
                device.exposureMode = .continuousAutoExposure
            }
            if device.isAutoFocusRangeRestrictionSupported {
                device.autoFocusRangeRestriction = .near
            }
            device.unlockForConfiguration()
            if userInitiated {
                animateFocusIndicator(at: viewPoint)
                statusLabel?.text = "Focused — capture when the label looks sharp"
            }
        } catch {
            print("LayIt label OCR focus adjustment failed: \(error.localizedDescription)")
        }
    }

    private func animateFocusIndicator(at point: CGPoint) {
        guard let focusIndicatorView = focusIndicatorView else { return }
        focusIndicatorView.center = point
        focusIndicatorView.transform = CGAffineTransform(scaleX: 1.2, y: 1.2)
        focusIndicatorView.alpha = 1
        UIView.animate(withDuration: 0.25, animations: {
            focusIndicatorView.transform = .identity
        }) { _ in
            UIView.animate(withDuration: 0.25, delay: 0.5, options: [.curveEaseOut]) {
                focusIndicatorView.alpha = 0
            }
        }
    }

    @objc private func subjectAreaDidChange() {
        focusCamera(at: CGPoint(x: view.bounds.midX, y: view.bounds.midY), userInitiated: false)
    }

    private func showError(_ msg: String) {
        let label = UILabel()
        label.text = msg
        label.textColor = .white
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func cancelTapped() {
        captureSession?.stopRunning()
        onCancel?()
        dismiss(animated: true)
    }

    @objc private func captureTapped() {
        guard !isCapturingPhoto else { return }
        isCapturingPhoto = true
        captureButton?.isEnabled = false
        statusLabel?.text = "Reading label..."

        let settings = AVCapturePhotoSettings()
        settings.flashMode = .off
        if let connection = photoOutput.connection(with: .video), connection.isVideoOrientationSupported {
            connection.videoOrientation = .portrait
        }
        photoOutput.capturePhoto(with: settings, delegate: self)
    }

    func photoOutput(_ output: AVCapturePhotoOutput,
                     didFinishProcessingPhoto photo: AVCapturePhoto,
                     error: Error?) {
        if let error = error {
            statusLabel?.text = "Capture failed. Try again."
            captureButton?.isEnabled = true
            isCapturingPhoto = false
            print("LayIt label OCR photo capture error: \(error.localizedDescription)")
            return
        }
        guard let cgImage = photo.cgImageRepresentation() else {
            statusLabel?.text = "Could not read photo. Try again."
            captureButton?.isEnabled = true
            isCapturingPhoto = false
            return
        }
        let imageBase64 = photo.fileDataRepresentation()?.base64EncodedString()

        let textRequest = VNRecognizeTextRequest()
        textRequest.recognitionLevel = .accurate
        textRequest.usesLanguageCorrection = false

        let barcodeRequest = VNDetectBarcodesRequest()
        barcodeRequest.symbologies = [.ean13, .ean8, .upce, .code128, .code39, .code93, .i2of5]

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([textRequest, barcodeRequest])

                let textObservations = textRequest.results ?? []
                let sortedObservations = textObservations.sorted {
                    let yDiff = abs($0.boundingBox.maxY - $1.boundingBox.maxY)
                    if yDiff > 0.03 {
                        return $0.boundingBox.maxY > $1.boundingBox.maxY
                    }
                    return $0.boundingBox.minX < $1.boundingBox.minX
                }
                let lines = sortedObservations.compactMap { $0.topCandidates(1).first?.string.trimmingCharacters(in: .whitespacesAndNewlines) }
                    .filter { !$0.isEmpty }
                let text = lines.joined(separator: "\n")

                let barcodeObservations = barcodeRequest.results ?? []
                let barcode = barcodeObservations
                    .compactMap { $0.payloadStringValue?.trimmingCharacters(in: .whitespacesAndNewlines) }
                    .first(where: { !$0.isEmpty })

                DispatchQueue.main.async {
                    if text.isEmpty && barcode == nil {
                        self.statusLabel?.text = "No readable label found. Try again."
                        self.captureButton?.isEnabled = true
                        self.isCapturingPhoto = false
                        return
                    }

                    self.captureSession?.stopRunning()
                    let generator = UINotificationFeedbackGenerator()
                    generator.notificationOccurred(.success)

                    self.statusLabel?.text = "Label read"
                    let payload = LabelScanPayload(text: text, barcode: barcode, imageBase64: imageBase64)
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { [weak self] in
                        self?.onResult?(payload)
                        self?.dismiss(animated: true)
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusLabel?.text = "Read failed. Try again."
                    self.captureButton?.isEnabled = true
                    self.isCapturingPhoto = false
                }
                print("LayIt label OCR Vision error: \(error.localizedDescription)")
            }
        }
    }
}
