//
//  ViewController.swift
//  ARKitPointCloudRecorder
//
//  Copyright © 2019 CurvSurf. All rights reserved.
//

import UIKit
import Metal
import MetalKit
import SceneKit
import ARKit
import CoreVideo

extension MTKView : RenderDestinationProvider {
}

class ViewController: UIViewController, MTKViewDelegate, ARSessionDelegate, ARSCNViewDelegate {
    
    @IBOutlet weak var labelPointCount: UILabel!
    @IBOutlet weak var recordBtn: UIButton!

    var session: ARSession!
    var renderer: Renderer!
    
    var isRecording: Bool = false
    
    var recorder: ARPointRecorder! = ARPointRecorder()
    var recorder_queue = DispatchQueue(label: "ARPointRecorder", attributes: [], autoreleaseFrequency: .workItem) // serial queue
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Set the view's delegate
        session = ARSession()
        session.delegate = self
        
        // Set the view to use the default device
        if let view = self.view as? MTKView {
            view.device = MTLCreateSystemDefaultDevice()
            view.backgroundColor = UIColor.clear
            view.delegate = self
            
            guard view.device != nil else {
                print("Metal is not supported on this device")
                return
            }
            
            // Configure the renderer to draw to the view
            renderer = Renderer(session: session, metalDevice: view.device!, renderDestination: view)
            renderer.drawRectResized(size: view.bounds.size)
        }
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        runSession()
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        
        // Pause the view's session
        session.pause()
//        sceneView.session.pause()
    }
    

    // MARK: - MTKViewDelegate
    
    // Called whenever view changes orientation or layout is changed
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        renderer.drawRectResized(size: size)
    }
    
    // Called whenever the view needs to render
    func draw(in view: MTKView) {
        renderer.update() // Draw camera image & feature points
        
        // Update UI -> # of feature points & camera tracking state
        var point_count = 0
        if let currentFrame = session.currentFrame {
            if let features = currentFrame.rawFeaturePoints {
                point_count = features.points.count
            }
            
            switch currentFrame.camera.trackingState
            {
            case .normal:
                labelPointCount.textColor = UIColor.green
            case .notAvailable:
                labelPointCount.textColor = UIColor.red
            case .limited(.excessiveMotion):
                labelPointCount.textColor = UIColor.yellow
            case .limited(.insufficientFeatures):
                labelPointCount.textColor = UIColor.orange
            case .limited(.initializing):
                labelPointCount.textColor = UIColor.white
            default:
                labelPointCount.textColor = UIColor.black
            }
        }
        
        labelPointCount.text = point_count > 0 ? String(format: "%d", point_count) : "0"
    }
    
    private func getDocumentDirectoryURL() -> URL?
    {
        let fm  = FileManager.default
        let df  = DateFormatter()
        let now = Date();
        
        df.dateFormat = "yyyyMMdd"
        let dateStr = df.string(from: now);
        
        df.dateFormat = "HH_mm_ss"
        let timeStr = df.string(from: now);
        
        let docURL = fm.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let dstDirURL: URL = docURL.appendingPathComponent( dateStr, isDirectory: true ).appendingPathComponent( timeStr )
        
        var isDir: ObjCBool = ObjCBool(false);
        if !fm.fileExists(atPath: dstDirURL.path, isDirectory: &isDir)
        {
            do {
                try fm.createDirectory(at: dstDirURL, withIntermediateDirectories: true, attributes: nil)
            }
            catch {
                print("Failed: FileManager.createDirectory(): [\(dstDirURL.path)]: \(error)")
                return nil
            }
        }
        else if !isDir.boolValue
        {
            print("[\(dstDirURL.path)]: Target path is already exist as a regular file")
            return nil
        }
        
        return dstDirURL
    }
    
    // MARK: - ARSessionDelegate
    
    
    
    // Record the CAMERA MOTION 4X4 MATRIX and Camer Intrinsics 3x3 FOR EACT FRAME
    var cameraMotion = [simd_float4x4]()
    var cameraIntrinsics = [simd_float3x3]()
    var ptArray = [[Float]]()

    // Called whenever the ARFrame has been updated
    var frameNum = 0
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        if isRecording {
            if let features = frame.rawFeaturePoints {
                switch frame.camera.trackingState {
                case .normal:
                    frameNum += 1
//                    if frameNum % 30 == 0 {
                        // APPEND MATRIX OF THE CURRENT FRAM TO THE CAMERA MOTION MATRIX
//                        let temp = frame.camera.transform
//                        cameraMotion.append(temp)
                        // CAPTURED IMAGE and get the pointer pointing to it
//                        let imageBuffer = frame.capturedImage
//                        CVPixelBufferLockBaseAddress(imageBuffer, [])
//                        let ptr = CVPixelBufferGetBaseAddress(imageBuffer)!
//                        let cnt = CVPixelBufferGetDataSize(imageBuffer)
//                        cameraIntrinsics.append(frame.camera.intrinsics)
//                        let saveCV = Data(bytes: ptr, count: cnt)
//                        let fileURL = try! FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false).appendingPathComponent("test_\(frameNum)")
//                        do {
//                            try saveCV.write(to: fileURL, options: .atomic)
//                        } catch {
//                            print(error)
//                        }
                        print("MOTION LEN: \(cameraMotion.count)")
                        print("INTR LEN: \(cameraIntrinsics.count)")
                    let ids = features.identifiers
                    for i in 0..<features.points.count{
//                        for pt in features.points {
                        let pt = features.points[i]
                            let ptTemp = [Float(frameNum), pt.x, pt.y, pt.z, Float(ids[i])]
                            ptArray.append(ptTemp)
                        }
//                    }
//                    recorder.appendPoints(from: features)
//                    let now = Date();
//                    let df = DateFormatter();
//                    df.dateFormat = "yyyy_MM_dd_HH_mm_ss";
//                    let nowStr = df.string(from: now)
//                    let dstURL = self.getDocumentDirectoryURL()
//                    let fullFileURL = dstURL?.appendingPathComponent( "\(nowStr)_full.txt" )
//                    recorder.saveFullPoints(to: fullFileURL?.path)
                    self.recorder.reset();
                default:
                    break
                }
            }
        }
    }
    
    func session(_ session: ARSession, didFailWithError error: Error) {
        // Present an error message to the user
        guard error is ARError else { return }
        
        let errorWithInfo = error as NSError
        let messages = [
            errorWithInfo.localizedDescription,
            errorWithInfo.localizedFailureReason,
            errorWithInfo.localizedRecoverySuggestion
        ]
        
        // Remove optional error messages.
        let errorMessage = messages.compactMap({ $0 }).joined(separator: "\n")
        
        DispatchQueue.main.async {
            // Present an alert informing about the error that has occurred.
            let alertController = UIAlertController(title: "The AR session failed.", message: errorMessage, preferredStyle: .alert)
            let restartAction = UIAlertAction(title: "Restart Session", style: .default) { _ in
                alertController.dismiss(animated: true, completion: nil)
                self.runSession(withReset: true)
            }
            alertController.addAction(restartAction)
            self.present(alertController, animated: true, completion: nil)
        }
        
    }
    
    func sessionWasInterrupted(_ session: ARSession) {
        // Inform the user that the session has been interrupted, for example, by presenting an overlay
        
    }
    
    func sessionInterruptionEnded(_ session: ARSession) {
        // Reset tracking and/or remove existing anchors if consistent tracking is required
        runSession(withReset: true)
    }
    
    
    
    // MARK: - private functions
    
    private func runSession(withReset _reset: Bool = false)
    {
        // Create a session configuration
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        
        let options: ARSession.RunOptions = _reset ? [.resetTracking, .removeExistingAnchors] : []
        session.run(configuration, options: options)
        
    }
    
    
    
    // MARK: - Event
    
    @IBAction func onClickRecord(_ sender: Any) {
        isRecording = !isRecording
        
        if isRecording { // start recording
            recorder.reset() // clear prev. data
            recordBtn.setTitle("Stop", for: .normal)
        }
        else { // stop recording
            recordBtn.isEnabled = false
            recordBtn.isHidden = true
            
            recorder_queue.async {
                // Save Recording Result to File
                if let dstURL = self.getDocumentDirectoryURL()
                {
                    let now = Date();
                    let df = DateFormatter();
                    df.dateFormat = "yyyy_MM_dd_HH_mm_ss";
                    
                    let nowStr = df.string(from: now)
                    
                    // SAVE THE CAMERA MOTION MATRIX
//                    let camMo = String("\(self.cameraMotion)")
//                    let fileURL = try! FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false).appendingPathComponent("cameraMotion.txt")
//
//                    do {
//                        try camMo.write(to: fileURL, atomically: true, encoding: String.Encoding.utf8)
//                    } catch {
//                        print(error)
//                    }
                    
                    // SAVE THE CAMERA INTRINSICS
//                    let camInt = String("\(self.cameraIntrinsics)")
//                    let fileURL2 = try! FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false).appendingPathComponent("cameraIntrinsics.txt")
//
//                    do {
//                        try camInt.write(to: fileURL2, atomically: true, encoding: String.Encoding.utf8)
//                    } catch {
//                        print(error)
//                    }
                    let pcdArr = String("\(self.ptArray)")
                    let pointfileURL2 = try! FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false).appendingPathComponent("pcdCloud.txt")
                    
                    do {
                        try pcdArr.write(to: pointfileURL2, atomically: true, encoding: String.Encoding.utf8)
                    } catch {
                        print(error)
                    }
                    self.frameNum = 0
                    self.ptArray = [[Float]]()
                }
                
                // Update UI after Saving Files
                DispatchQueue.main.async{
                    self.recordBtn.isHidden = false
                    self.recordBtn.isEnabled = true
                    self.recordBtn.setTitle("Record", for: .normal)
                }
            }
        }
    }
    
    @IBAction func onClickReset(_ sender: Any) {
        runSession(withReset: true)
    }
}

