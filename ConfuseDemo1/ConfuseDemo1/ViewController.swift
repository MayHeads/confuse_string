//
//  ViewController.swift
//  ConfuseDemo1
//
//  Created by mayheaders on 2025/6/5.
//

import UIKit
import SwifterSwift

class ViewController: UIViewController {
    
    var lxvIewx = UIColor.init(hexString: "x01111")

    override func viewDidLoad() {
        super.viewDidLoad()
        
        print(xc)
        print(xy1)
        print(xy2)
        
        
        ysEventTrace(name: "page_view", argument: [
            "page_name" : "首页",
        ])
    }
    
    func ysEventTrace(name: String, argument: [String: Any]) {
        
    }


}


class NoteGuideModel {
    var souce: String
    var title: String
    var tips: String
    var indiImage: String
    
    init(souce: String, title: String, tips: String, indiImage: String) {
        self.souce = souce
        self.title = title
        self.tips = tips
        self.indiImage = indiImage
    }
     
    static let allItems: [NoteGuideModel] = [
        NoteGuideModel.init(souce: "3s", title: "gu1", tips: "gut1", indiImage: "indi_1"),
        NoteGuideModel.init(souce: "cleansame", title: "gu2", tips: "gut2", indiImage: "indi_2"),
        NoteGuideModel.init(souce: "cleanbigvideo", title: "gu3", tips: "gut3", indiImage: "indi_3"),
    ]
}


