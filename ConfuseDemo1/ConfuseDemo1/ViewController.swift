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
        
        let fixString = k == true ? "home_clear_apple" : "home_clear_sensor"
        
        
        let x1 = UIImageView(image: imagg3)
        x1.contentMode = .scaleAspectFit
        view.addSubview(x1)
        x1.frame = CGRectMake(20, 100, 100, 100)


    }
    
    func ysEventTrace(name: String, argument: [String: Any]) {
        
    }
    
    var totalStorageGBValue: Float {
        return (Float("1234".replacingOccurrences(of: ",", with: "")) ?? 0) / 1000.0
    }
    
    var titles = ["非常满意", "满意", "一般", "不满意"]


    let items = ["外网 IP", "外网 IP", "外网 IP"]
    
    let k: Bool = false

    
    
    let iamge2 = UIImage.init(named: "duc_4lrg7v")
    
    let imagg3 = UIImage.init(named: "duc_uo9404")
    
    
    
 

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


extension Double {
    
    var dataBytesAndUnit: (String,String) {
        
        let fileSize1 = CGFloat(self)
        let KB:CGFloat = 1024
        let MB:CGFloat = KB*KB
        let GB:CGFloat = MB*KB
        
        if self < 10 {
            return ("0.00","B")
            
        } else if fileSize1 < KB {
            return ("< 1 ","KB")
        } else if fileSize1 < MB {
            return (String(format: "%.2f", CGFloat(fileSize1)/KB),"KB")
        } else if fileSize1 < GB {
            return (String(format: "%.2f", CGFloat(fileSize1)/MB),"MB")
        } else {
            return (String(format: "%.2f", CGFloat(fileSize1)/GB),"GB")
        }
    }
}


