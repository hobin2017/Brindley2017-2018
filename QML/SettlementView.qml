import QtQuick 2.9
import MyModel 1.0
import QtGraphicalEffects 1.0
Item {
    id:settlement
    property double allprice: 0.0
    property string userName: "NoneName"
    property int number: 0
    property double backOpacity: 1

    property alias pic1 : pic1
    property alias pic2 : pic2
    property alias pic3 : pic3
    property alias pic4 : pic4

    property alias name1: name1
    property alias name2: name2
    property alias name3: name3
    property alias name4: name4

    property alias pric1: pric1
    property alias pric2: pric2
    property alias pric3: pric3
    property alias pric4: pric4

    property alias headPic: headPic
    property alias littleApp: littleApp
    property alias lightInfo: lightInfo

    FontLoader { id: siyuanhei; source: "../font/siyuanheiti.ttf" }


    function getCameraPersion(){
        return testCustomOpenCVItem
    }
    function stopCamera(){
       // testCustomOpenCVItem.isPaint = false
    }
    function toFacePay(){
        aroundPic.visible = true
        stopCamera()
        aroundPic.opacity = 1
        tipsText.text = qsTr("会员人脸支付")
        tipsText.visible = true
        cameraItem.visible = false

        headPicItem.visible = true
        headPicItem.y = 70
        payingItem.visible = true
        payingItem.opacity = 1
    }

    function toRegister(){
        tipsText.text = qsTr("首次使用人脸支付")
        tipsText.visible = true
        payingItem.opacity = 0
        payingItem.visible = true
        var t = headPicItem.width * 0.6
        headPicItem.width = t
        headPicItem.height = t
        aroundPic.opacity = 0
        faceregister.visible = true
        faceregister.opacity = 1
        timerRegister.start()
    }
    function toPaySuccess(){
        payingItem.opacity = 0

        faceregister.opacity = 0
        paySuccess.opacity = 1

        tipsText.text = qsTr("会员人脸支付")
        tipsText.visible = true
        var t = headPicItem.parent.width*0.4
        headPicItem.width = t
        headPicItem.height = t
        userNameItem.visible = true
        aroundPic.visible = false
        var tt = successImage.parent.width*0.4
        successImage.width = tt
        successImage.height =tt

        payingItem.visible = true
    }

    function toPayFail(){
        payingItem.opacity = 0

        faceregister.opacity = 0
        payFail.opacity = 1
        aroundPic.visible = false
        tipsText.text = qsTr("会员人脸支付")
        tipsText.visible = true
        var t = headPicItem.parent.width*0.4
        headPicItem.width = t
        headPicItem.height = t
        userNameItem.visible = true

        var tt = filImage.parent.width*0.4
        filImage.width = tt
        filImage.height =tt

        payingItem.visible = true
    }


    function resetSettlement(){
        visible = false
        timerRegister.stop()
        faceregister.timestr = 30
        headPicItem.reset()

        successImage.width = 1
        successImage.height =1
        paySuccess.opacity = 0



        filImage.width = 1
        filImage.height =1
        payFail.opacity = 0

        faceregister.visible = false

        cameraItem.visible = true
        tipsText.visible = false
        payingItem.visible = false
        payingItem.opacity = 0
        cleanCommodity()
        restFinish()
    }


    function cleanCommodity(){
        pic1.height = 1
        pic1.width = 1
        name1.text = qsTr("")
        pric1.text = qsTr("")

        pic2.height = 1
        pic2.width = 1
        name2.text = qsTr("")
        pric2.text = qsTr("")

        pic3.height = 1
        pic3.width = 1
        name3.text = qsTr("")
        pric3.text = qsTr("")

        pic4.height = 1
        pic4.width = 1
        name4.text = qsTr("")
        pric4.text = qsTr("")
    }





    signal restFinish()



    Grid{
        id:commdGrid
        anchors.left: parent.left
        anchors.right: rightItem.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: parent.width*0.05
        anchors.topMargin: parent.width*0.03
        anchors.bottomMargin: parent.width*0.06
        spacing: height*0.05
        columns: 2
        rows:2
        Image {
            width: parent.width*0.5
            height: parent.height*0.45
            source:"../Images/background.png"
            opacity:backOpacity
            Item{
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.08
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.top: parent.top
                anchors.topMargin: parent.width*0.05
                height: parent.height*0.70
                CommodityPicItem{
                    id:pic1
                    anchors.centerIn: parent
                    width:1
                    height:1
                    Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    onSetImageSignal:{
                        visible=false
                        width = 1
                        height = 1
                        visible=true
                        width = parent.width
                        height = parent.height
                    }
                }
                MouseArea{
                    anchors.fill:parent
                    onClicked: {
                        pic1.setCommodImage("define")
                    }
                }
            }
            Text {
                id:name1
                color: "#09BB07"
                text: qsTr("鸭脖")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.15
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
            Text {
                id:pric1
                text: qsTr("￥11.50")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
        }
        Image {
            width: parent.width*0.5
            height: parent.height*0.45
            source:"../Images/background.png"
            opacity:backOpacity
            Item{
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.08
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.top: parent.top
                anchors.topMargin: parent.width*0.05
                height: parent.height*0.70
                CommodityPicItem{
                    id:pic2
                    anchors.centerIn: parent
                    width:1
                    height:1
                    Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    onSetImageSignal:{
                        visible=false
                        width = 1
                        height = 1
                        visible=true
                        width = parent.width
                        height = parent.height
                    }
                }
                MouseArea{
                    anchors.fill:parent
                    onClicked: {
                        pic2.setCommodImage("define")
                    }
                }
            }
            Text {
                id:name2
                color: "#09BB07"
                text: qsTr("鸭脖")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.15
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
            Text {
                id:pric2
                text: qsTr("￥11.50")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
        }
        Image {
            width: parent.width*0.5
            height: parent.height*0.45
            source:"../Images/background.png"
            opacity:backOpacity
            Item{
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.08
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.top: parent.top
                anchors.topMargin: parent.width*0.05
                height: parent.height*0.70
                CommodityPicItem{
                    id:pic3
                    anchors.centerIn: parent
                    width:1
                    height:1
                    Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    onSetImageSignal:{
                        visible=false
                        width = 1
                        height = 1
                        visible=true
                        width = parent.width
                        height = parent.height
                    }
                }
                MouseArea{
                    anchors.fill:parent
                    onClicked: {
                        pic3.setCommodImage("define")
                    }
                }
            }
            Text {
                id:name3
                color: "#09BB07"
                text: qsTr("鸭脖")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.15
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
            Text {
                id:pric3
                text: qsTr("￥11.50")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
        }
        Image {
            width: parent.width*0.5
            height: parent.height*0.45
            source:"../Images/background.png"
            opacity:backOpacity
            Item{
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.08
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.top: parent.top
                anchors.topMargin: parent.width*0.05
                height: parent.height*0.70
                CommodityPicItem{
                    id:pic4
                    anchors.centerIn: parent
                    width:1
                    height:1
                    Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    onSetImageSignal:{
                        visible=false
                        width = 1
                        height = 1
                        visible=true
                        width = parent.width
                        height = parent.height
                    }
                }
                MouseArea{
                    anchors.fill:parent
                    onClicked: {
                        pic4.setCommodImage("define")
                    }
                }
            }
            Text {
                id:name4
                color: "#09BB07"
                text: qsTr("鸭脖")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.10
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
            Text {
                id:pric4
                text: qsTr("￥11.50")
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 18
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.08
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height*0.05
            }
        }
    }

    //右边栏
    Rectangle{
        id:rightItem
        anchors.fill: parent
        anchors.leftMargin: parent.width*0.73
        color: "#09BB07"

        Text {
            id:tipsText
            color: "#ffffff"
            visible: false
            text: qsTr("")
            font.family: siyuanhei.name
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.pointSize: 25
            anchors.top:parent.top
            anchors.topMargin: parent.height*0.10
            anchors.horizontalCenter: parent.horizontalCenter
            onTextChanged: {
                visible = true
            }
        }



        //摄像头模块
        Item {
            id:cameraItem
            anchors.fill: parent
            anchors.leftMargin: parent.width*0.04
            anchors.rightMargin: parent.width*0.04

            Text {
                color: "#ffffff"
                text: qsTr("支付金额")
                font.pointSize: 17
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter

                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: parent.height*0.1
            }

            Text {
                id:sumPrice
                color: "#ffffff"
                text: qsTr("￥"+allprice)
                font.pointSize: 40
                font.family: siyuanhei.name
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter

                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: parent.height*0.19
            }



            Image {
                id: wline
                source: "../Images/wline.png"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: parent.height*0.34
                width: parent.width
                height: 3
                fillMode: Image.PreserveAspectFit
            }


            onVisibleChanged: {
                if(visible==false){
                   // testCustomOpenCVItem.isPaint = false
                }else{
                   // testCustomOpenCVItem.isPaint = true
                }
            }

            Rectangle{
                id: mask
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: parent.height*0.38

                width:parent.width
                height:width*0.75
                color: "#0009BB07"
                CustomOpenCVItem {
                    id: testCustomOpenCVItem
                    anchors.fill: parent
                    //cameraID: 0
                    //visible: false
                    activateVideo: true
                    //activateFaceRecognition: settings.facialRecognitionActive
                    //property string myColor: "green"
                }
            }
            Text {
                id: lightInfo
                font.family: siyuanhei.name
                text: qsTr("还未能识别面部，可适当挪动一下位置。")
                font.pointSize: 14
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: tipsPic.top
                anchors.bottomMargin: 2
                color: "#ffffff"
                opacity:0
                Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }
                onOpacityChanged: {
                    if(opacity == 1){
                        lightInfoTimer.start()
                    }
                }
                Timer{
                    id:lightInfoTimer
                    interval: 1600; running: false; repeat: false
                    onTriggered: {
                        parent.opacity = 0
                    }
                }
            }

            Image {
                id: tipsPic
                source: "../Images/handtips.png"
                fillMode: Image.PreserveAspectFit
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 35
                width:parent.width
                height: parent.height*0.23
            }
            Text {
                color: "#ffffff"
                text: qsTr("手势\"点赞\"，提交订单")
                font.family: siyuanhei.name
                font.pointSize: 15
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 5
            }
        }




        //提示
        Item {
            id: tipsItem
            opacity : 1
            anchors.fill: parent
            anchors.topMargin: parent.width*0.33
            anchors.leftMargin: parent.width*0.1
            anchors.rightMargin: parent.width*0.1
            anchors.bottomMargin: parent.height*0.1
            Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }

            //支付成功
            Item{
                id:paySuccess
                opacity : 0
                Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }

                anchors.horizontalCenter: parent.horizontalCenter
                y : parent.height * 0.6
                width:parent.width*0.8
                height: parent.height*0.4
                Image{
                    id:successImage
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.1
                    source: "../Images/ok_g2.png"
                    width: 1
                    fillMode: Image.PreserveAspectFit
                    height: 1
                    Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                }
                Text {
                    text: qsTr("支付完成")
                    font.family: siyuanhei.name
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 23
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.85
                    color: "#ffffff"
                }

            }

            //支付失败
            Item {
                id: payFail
                anchors.horizontalCenter: parent.horizontalCenter
                y : parent.height * 0.6
                width:parent.width*0.8
                height: parent.height*0.4
                opacity : 0
                Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }

                Image {
                    id:filImage
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.1
                    source: "../Images/worring_g.png"
                    fillMode: Image.PreserveAspectFit
                    width: 1
                    height: 1
                    Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                    Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                }
                Text {
                    text: qsTr("支付失败")
                    font.family: siyuanhei.name
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 23
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.55
                    color: "#ffffff"
                }
                Text {
                    text: qsTr("疑似微信支付额度不足\n或今日免密支付金额达到上限")
                    font.family: siyuanhei.name
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 18
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.85
                    color: "#ffffff"
                }
            }


            //会员人脸
            Item{
                id:headPicItem
                anchors.horizontalCenter: parent.horizontalCenter
                y : parent.height*0.8
                width:parent.width*0.4
                height:width
                function reset(){
                    y = headPicItem.parent.height*0.8
                    var t = headPicItem.parent.width*0.4
                    headPicItem.width = t
                    headPicItem.height = t
                    headPicItem.visible = false
                    userNameItem.visible = false
                }
                Behavior on y {PropertyAnimation { easing.overshoot: 0.4; easing.type: Easing.OutBack;duration: 500} }
                Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
                visible:false
                PicItem{
                    id:headPic
                    anchors.fill:parent
                    visible:true
                }



                AnimatedImage{
                    id:aroundPic
                    anchors.centerIn:  parent
                    height: parent.height*1.2
                    width: height*1.77
                    source: "../Images/headaround.gif"
                    fillMode: Image.PreserveAspectFit
                    Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }

                }
                Text {
                    id: userNameItem
                    color: "#ffffff"
                    text: qsTr(userName)
                    font.family: siyuanhei.name
                    visible: false
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 17
                    anchors.horizontalCenter: parent.horizontalCenter
                    y :parent.height*1.25
                }
            }


            //正在支付
            Item{
                id:payingItem
                opacity : 0
                visible:false
                Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }
                anchors.horizontalCenter: parent.horizontalCenter
                y : parent.height * 0.6
                width:parent.width*0.8
                height: parent.height*0.4
                Text {
                    text: qsTr("支付中")
                    font.family: siyuanhei.name
                    color: "#ffffff"
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 15
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.80
                }
                AnimatedImage{

                    opacity : 1
                    Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }
                    anchors.horizontalCenter: parent.horizontalCenter
                    y:parent.height*0.80
                    source: "../Images/paying.gif"
                    width: parent.width*0.4
                    fillMode: Image.PreserveAspectFit
                    height: width
                }
            }



            //会员注册
            Item {
                id: faceregister
                anchors.horizontalCenter: parent.horizontalCenter
                y : parent.height * 0.3
                width:parent.width*0.8
                height: parent.height
                opacity: 0
                property int timestr: 30
                Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }

                Text {
                    text: qsTr("请扫码完善信息，开启人脸支付")
                    font.family: siyuanhei.name
                    font.pointSize: 20
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    y:0
                    color: "#ffffff"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                PicItem {
                    id:littleApp
                    width: parent.width
                    height: width
                    y:parent.height*0.25
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                Text {
                    id: limitText
                    color: "#ffffff"
                    text: qsTr(parent.timestr+"秒")
                    font.family: siyuanhei.name
                    font.pointSize: 19
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: parent.height*0.2
                }
                Timer{
                    id:timerRegister
                    interval: 1000; running: false; repeat: true
                    onTriggered: {
                        parent.timestr-=1
                        if(parent.timestr == 0){
                            stop()
                            parent.timestr = 30
                            parent.parent.parent.parent.resetSettlement()
                        }
                    }
                }
            }

            Behavior on opacity {PropertyAnimation {duration: 1000} }

        }
    }

}
