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
            photoOutput.isHighResolutionCaptureEnabled = true
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
        settings.isHighResolutionPhotoEnabled = true
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
        guard let cgImage = photo.cgImageRepresentation()?.takeUnretainedValue() else {
            statusLabel?.text = "Could not read photo. Try again."
            captureButton?.isEnabled = true
            isCapturingPhoto = false
            return
        }

        let request = VNDetectBarcodesRequest()
        request.symbologies = [.EAN13, .EAN8, .UPCE, .Code128, .Code39, .Code93, .I2of5]

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([request])
                let observations = request.results as? [VNBarcodeObservation] ?? []
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
