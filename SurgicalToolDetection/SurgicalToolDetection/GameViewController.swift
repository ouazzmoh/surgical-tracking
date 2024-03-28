//
//  GameViewController.swift
//  SurgicalToolDetection
//
//  Created by Hafize Nur Şahbudak on 06.03.24.
//

import UIKit
import QuartzCore
import SceneKit

class GameViewController: UIViewController {
    
    @IBOutlet var scnView: SCNView!
    var boxNode: SCNNode?
    var forcepsNode: SCNNode?
    var networkController: NetworkController?
    var cameraStandScale: Float!
    var boxScale: CGFloat!
    var forcepsScale: Float!
    var diagonalofStand: Float! = 0
    
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupScale()
        setupView()
        setupNetworkCommunication()
        
    }
    func setupScale() {
        cameraStandScale = 0.001
        forcepsScale = 0.01
        boxScale = 0.1
    }
    
    func setupView() {
        // create a new scene
        //let scene = SCNScene(named: "art.scnassets/cameraStand.scn")!
        let scene = SCNScene(named: "art.scnassets/cameraStand.scn")!
        
        // create and add a camera to the scene
        let cameraNode = SCNNode()
        cameraNode.camera = SCNCamera()
        scene.rootNode.addChildNode(cameraNode)
        
        // place the camera
        cameraNode.position = SCNVector3(x: 0, y: 0, z: 5)
        
        // create and add a light to the scene
        let lightNode = SCNNode()
        lightNode.light = SCNLight()
        lightNode.light!.type = .omni
        lightNode.position = SCNVector3(x: 0, y: 10, z: 10)
        scene.rootNode.addChildNode(lightNode)
        
        // create and add an ambient light to the scene
        let ambientLightNode = SCNNode()
        ambientLightNode.light = SCNLight()
        ambientLightNode.light!.type = .ambient
        ambientLightNode.light!.color = UIColor.darkGray
        scene.rootNode.addChildNode(ambientLightNode)
        
        // Create a red box
        //        let boxGeometry = SCNBox(width: boxScale,
        //                                 height: boxScale,
        //                                 length: boxScale,
        //                                 chamferRadius: 0.0)
        //        let material = SCNMaterial()
        //        material.diffuse.contents = UIColor.red
        //        boxGeometry.materials = [material]
        //        boxNode = SCNNode(geometry: boxGeometry)
        //        boxNode?.position = SCNVector3(x: 0, y: 0.5, z: 0)
        //        if let boxNode = boxNode {
        //            scene.rootNode.addChildNode(boxNode)
        //        }
        
        // Set the scene to the view
        scnView.scene = scene
        scnView.allowsCameraControl = true
        scnView.showsStatistics = true
        scnView.backgroundColor = UIColor.black
        
        
        // retrieve the cameraStand node
        if let cameraStand
            = scene.rootNode.childNode(withName: "cameraStand", recursively: true) {
            // animate the 3d object
            //cameraStand.runAction(SCNAction.repeatForever(SCNAction.rotateBy(x: 0, y: 2, z: 0, duration: 1)))
            cameraStand.scale = SCNVector3(x: cameraStandScale,
                                           y: cameraStandScale,
                                           z: cameraStandScale)
            let boundingBox = cameraStand.boundingBox
            
            // Calculate the width and height
            let width = boundingBox.max.x - boundingBox.min.x
            let height = boundingBox.max.y - boundingBox.min.y
            
            diagonalofStand = sqrt(width*width + height*height) / 2 * cameraStandScale
            
            cameraStand.position = SCNVector3(x: 0, y: 0, z: diagonalofStand)
        } else {
            print("Node 'cameraStand' not found in the scene")
        }
        
        if let forcepsRedGreen
            = scene.rootNode.childNode(withName: "forcepsRedGreen", recursively: true) {
            // animate the 3d object
            //cameraStand.runAction(SCNAction.repeatForever(SCNAction.rotateBy(x: 0, y: 2, z: 0, duration: 1)))
            forcepsRedGreen.scale = SCNVector3(x: forcepsScale,
                                               y: forcepsScale,
                                               z: forcepsScale)
            let boundingBox = forcepsRedGreen.boundingBox
            
            forcepsRedGreen.position = SCNVector3(x: 0, y: 0, z: 0)
            
            let angleInRadians = 30.0 * (.pi / 180.0)
            forcepsRedGreen.eulerAngles.z = Float(angleInRadians)
            forcepsNode = forcepsRedGreen
        } else {
            print("Node 'forcepsRedGreen' not found in the scene")
        }
        
        
        // retrieve the SCNView
        let scnView = self.view as! SCNView
        
        // set the scene to the view
        scnView.scene = scene
        
        // allows the user to manipulate the camera
        scnView.allowsCameraControl = true
        
        // show statistics such as fps and timing information
        scnView.showsStatistics = true
        
        // configure the view
        scnView.backgroundColor = UIColor.black
        
        // add a tap gesture recognizer
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        scnView.addGestureRecognizer(tapGesture)
    }
    
    
    @objc
    func handleTap(_ gestureRecognize: UIGestureRecognizer) {
        // retrieve the SCNView
        let scnView = self.view as! SCNView
        
        // check what nodes are tapped
        let p = gestureRecognize.location(in: scnView)
        let hitResults = scnView.hitTest(p, options: [:])
        // check that we clicked on at least one object
        if hitResults.count > 0 {
            // retrieved the first clicked object
            let result = hitResults[0]
            
            // get its material
            let material = result.node.geometry!.firstMaterial!
            
            // highlight it
            SCNTransaction.begin()
            SCNTransaction.animationDuration = 0.5
            
            // on completion - unhighlight
            SCNTransaction.completionBlock = {
                SCNTransaction.begin()
                SCNTransaction.animationDuration = 0.5
                
                material.emission.contents = UIColor.black
                
                SCNTransaction.commit()
            }
            
            material.emission.contents = UIColor.red
            
            SCNTransaction.commit()
        }
    }
    
    override var prefersStatusBarHidden: Bool {
        return true
    }
    
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        if UIDevice.current.userInterfaceIdiom == .phone {
            return .allButUpsideDown
        } else {
            return .all
        }
    }
    
}

extension GameViewController {
    func setupNetworkCommunication() {
        // Simulate network communication by periodically fetching new coordinates
        networkController = NetworkController()
        //let localHost = "127.0.0.1"
        let csHost = "192.168.0.57"
        //let deneme = "0.0.0.0"
        
        networkController?.startConnection(host: csHost , port: 5555)
        networkController?.onDataReceived = { [weak self] coordinates in
            DispatchQueue.main.async {
                print(coordinates)
               // self?.updateForcepsposition(coordinates)
            }
        }
    }
    
    func updateRedBoxPosition(_ newPosition: SCNVector3) {
        // Update the red box's position with the new coordinates
        self.boxNode?.position = newPosition
        
    }
    
    func updateForcepsposition(_ newPosition: SCNVector3) {
       // self.forcepsNode?.position = newPosition
    }
    
    
}
