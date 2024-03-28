//
//  NetworkController.swift
//  SurgicalToolDetection
//
//  Created by Hafize Nur Şahbudak on 06.03.24.
//

import SceneKit

import Foundation
import Network

class NetworkController {
    var connection: NWConnection?
    var onDataReceived: ((SCNVector3) -> Void)?
    
    func startConnection(host: String, port: UInt16) {
        let hostEndpoint = NWEndpoint.Host(host)
        let portEndpoint = NWEndpoint.Port(rawValue: port)!
        
        connection = NWConnection(host: hostEndpoint, port: portEndpoint, using: .tcp)
        
        connection?.stateUpdateHandler = { [weak self] state in
            switch state {
            case .ready:
                print("Connected to server")
                self?.receiveData()
            default:
                break
            }
        }
        
        connection?.start(queue: .main)
    }
    
    private func receiveData() {
        connection?.receive(minimumIncompleteLength: 1, maximumLength: 1024) { [weak self] data, _, _, error in
            guard let data = data, error == nil, let self = self else {
                print("Error receiving data: \(error?.localizedDescription ?? "Unknown error")")
                return
            }
            
            if let message = String(data: data, encoding: .utf8),
               let coords = self.parseCoordinates(from: message) {
                self.onDataReceived?(coords)
            }
            
            self.receiveData()
        }
    }
    
    private func parseCoordinates(from message: String) -> SCNVector3? {
        // Attempt to deserialize the JSON string into an array of arrays
        guard let data = message.data(using: .utf8),
              let jsonArray = try? JSONSerialization.jsonObject(with: data) as? [[Double]],
              jsonArray.count == 3,
              let x = jsonArray[0].first,
              let y = jsonArray[1].first,
              let z = jsonArray[2].first else {
            print("Failed to parse coordinates from message: \(message)")
            return nil
        }

        // Convert Double to Float since SCNVector3 expects Float values
        return SCNVector3(x: -1*Float(x/100), y: Float(y/100), z: -1*Float(z/100))
    }
    
}
