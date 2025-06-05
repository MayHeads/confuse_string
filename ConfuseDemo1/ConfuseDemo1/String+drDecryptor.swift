//
//  String+drDecryptor.swift
//
//  Created on 2025/06/05
//

import Foundation
import CryptoSwift

extension String {
    enum StringDecrypt {
        static let key = "86eBpe59xO6vhXQe"
        static let iv = "86eBpe59xO6vhXQe"
    }
    
    func dr_decrypt() -> String{
        var text: String?
        do {
            let aes = try AES(key: StringDecrypt.key, iv: StringDecrypt.iv, padding: .pkcs5)
            let finiteCiphertext = try aes.decrypt(Array(base64: self))
            let backwardString = String(decoding: finiteCiphertext, as: UTF8.self)
            text = backwardString
        } catch {
        }
        return text ?? ""
    }

    func dr_encrypt() -> String? {
        var text = ""
        do {
            let aes = try AES(key: StringDecrypt.key, iv: StringDecrypt.iv, padding: .pkcs5)
            let finiteCiphertext = try aes.encrypt(Array(self.utf8))
            text = finiteCiphertext.toBase64()
        }
        catch {
        }
        return text
    }
    
}
