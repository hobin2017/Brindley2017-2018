import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Window 2.3
import QtQml 2.2
ApplicationWindow {
    id: window
    visible: true
    //visibility: Window.FullScreen
    visibility: Window.Maximized
    property alias settle: settle


    FontLoader { id: siyuanhei; source: "../font/siyuanheiti.ttf" }

    function toTooMuchCommodity(){

        identifing.visible = false
        identifing.opacity = 0
        wel.y = -wel.height
        payFinish.y = -payFinish.height
        devError.y = -devError.height
        showError(2)

    }

    function toCantidentified(){

        identifing.visible = false
        identifing.opacity = 0
        wel.y = -wel.height
        payFinish.y = -payFinish.height
        devError.y = -devError.height


    }

    function toIdentifing(){
        payFinish.y = -payFinish.height

        devError.y = -devError.height

        identifing.visible = true
        identifing.opacity = 1
        wel.y = -wel.height


    }

    function toWelComeView(){

        settle.resetSettlement()
        settle.visible = false

        payFinish.y = -payFinish.height

        devError.y = -devError.height
        identifing.visible = false
        identifing.opacity = 0
        wel.y = 0
    }

    function toSettlementView(){
        payFinish.y = -payFinish.height

        devError.y = -devError.height
        wel.y = -wel.height
        identifing.visible = false
        identifing.opacity = 0
        settle.resetSettlement()
        settle.visible = true
    }

    function getPicObject(id){
        switch(id){
            case 1:
                return settle.pic1
            case 2:
                return settle.pic2
            case 3:
                return settle.pic3
            case 4:
                return settle.pic4
        }
    }

    function setCommodity(id,name,price){
        switch(id){
        case 1:
            settle.name1.text = qsTr(name)
            settle.pric1.text = qsTr("￥"+price)
            break
        case 2:
            settle.name2.text = qsTr(name)
            settle.pric2.text = qsTr("￥"+price)
            break
        case 3:
            settle.name3.text = qsTr(name)
            settle.pric3.text = qsTr("￥"+price)
            break
        case 4:
            settle.name4.text = qsTr(name)
            settle.pric4.text = qsTr("￥"+price)
            break
        default:
            console.log("id:"+id+" error")
        }
    }

    function setSumPrice(price){
        settle.allprice = price
    }

    function getCameraPersionItem(){
        return settle.getCameraPersion()
    }

    function getHeadImage(){
        return settle.headPic
    }

    function toRegisterView(){
        settle.toRegister()
    }
    function toPaying(){
        settle.toFacePay()
    }
    function setUserName(str){
        settle.userName = str
    }

    function toPaySuccess(){
        settle.toPaySuccess()
    }

    function toPayFail(){
        settle.toPayFail()
    }

    function toLeaveStore(){

        settle.resetSettlement()
        payFinish.y=0
    }

    function getLittleApp(){
        return settle.littleApp
    }

    function showFaceCantIdentify(){
        settle.lightInfo.opacity = 1
    }

    function cleanCommodity(){
        settle.cleanCommodity()
    }


    function showError(i){
        errorItem.mode = i
    }
    function hideError(){
        errorItem.visible = false
    }


    onClosing: {
        settle.getCameraPersion().activateVideo = false

    }

    Rectangle{
        id:identifing
        width: parent.width
        height: parent.height
        x:0
        y:0
        visible: false
        Behavior on opacity {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 700} }
        opacity: 0
    /*    Text {
            color: "#09BB07"
            text: qsTr("正在识别")
            font.family: siyuanhei.name
            font.pointSize: 40
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: parent.height*0.18
        }*/
        onVisibleChanged: {
            if(visible==false){
                idgif.playing = false
            }else{
                idgif.playing = true
            }

        }
        AnimatedImage{
            id:idgif
            source: "../Images/Identifing.gif"
            anchors.fill: parent
	    anchors.margins:parent.height*0.3
            fillMode: Image.PreserveAspectFit
        }

    }


    SettlementView{
        anchors.fill: parent
        id:settle
        visible: false
    }



    //打包离店
    Rectangle{
        id:payFinish
        width: parent.width
        height: parent.height
        color: "#09BB07"
        x:0
        y:-height
        Behavior on y {PropertyAnimation { easing.amplitude: 0.2;  easing.type: Easing.OutBounce;duration: 1000}  }
        Image {
            source: "../Images/packge.png"
            width: parent.width*0.2
            height: parent.height*0.25
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
            y:parent.height*0.3
        }
        Text {
            color: "#ffffff"
            text: qsTr("请取下方的塑料袋，打包离店")
            font.family: siyuanhei.name
            font.pointSize: 25
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: parent.height*0.3
        }
    }




    WelcomeView{
        id:wel
        x:0
        y:0
        visible: true
        width: parent.width
        height: parent.height

        Behavior on y {PropertyAnimation { easing.amplitude: 0.2;  easing.type: Easing.OutBounce;duration: 1000} }

    }


    Rectangle{
        id:errorItem
        color: "#44000000"
        width: parent.width
        height: parent.height
        x:0
        y:0

        visible: false
        radius:10
        property int mode: -1
        onModeChanged: {
            console.log("mode change " + mode)
            switch(mode){
            case 0:
                errorItem.visible = true
                cantIdentify.visible = true
                devError.visible = false
                tooMuchCommity.visible = false
                break;
            case 1:
                errorItem.visible = true
                cantIdentify.visible = false
                devError.visible = true
                tooMuchCommity.visible = false
                break;
            case 2:
                errorItem.visible = true
                cantIdentify.visible = false
                devError.visible = false
                tooMuchCommity.visible = true
                break;
             default:
                 console.error("Unknow Error Number!")
            }
            mode = -1
        }

        Rectangle{
            id:cantIdentify

            anchors.centerIn: parent
            width: 1
            height: 1
            Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
            Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
            color: "#ffffff"
            radius:10
            visible: false
            onVisibleChanged: {
                if(visible==false){
                    width=1
                    height=1
                    unidgif.playing = false
                }else{
                    width= parent.width*0.6
                    height= parent.height*0.6
                    console.log(parent.width+" p: "+parent.height)
                    console.log(width+":"+height)
                    unidgif.playing = true
                }
            }

            AnimatedImage{
                id:unidgif
                anchors.fill: parent
                anchors.topMargin: parent.height*0.20
                anchors.bottomMargin: parent.height*0.1
                anchors.leftMargin: parent.height*0.1
                anchors.rightMargin: parent.height*0.1
                source: "../Images/unindefind.gif"
                fillMode: Image.PreserveAspectFit
            }
            Item{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top:parent.top
                anchors.topMargin: parent.height*0.02
                height: parent.height*0.16
                width: parent.width*0.8
                Image {
                    id:noiWorry
                    anchors.left: parent.left
                    anchors.leftMargin: parent.width*0.02
                    anchors.verticalCenter: parent.verticalCenter
                    source: "../Images/worring_w.png"
                    height:  window.height*0.08
                    fillMode: Image.PreserveAspectFit
                    width: height
                }
                Text {
                    anchors.right: parent.right
                    anchors.rightMargin: parent.width*0.1
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: noiWorry.right
                    anchors.leftMargin: parent.width*0.1
                    color: "#09BB07"
                    text: qsTr("商品未能识别,或商品重量有误。")
                    font.family: siyuanhei.name
                    font.pointSize: 30
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }


        Rectangle{
            id:devError
            anchors.centerIn: parent
            width: 1
            height: 1
            Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
            Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
            radius:10

            color: "#ffffff"
            visible: false
            onVisibleChanged: {
                if(visible==false){
                    width= 1
                    height: 1
                }else{
                    width= parent.width*0.4
                    height= parent.height*0.15
                }
            }

            Image {
                id:devWorry
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.05
                anchors.verticalCenter: parent.verticalCenter
                source: "../Images/worring_w.png"
                height: window.height*0.08
                width: height
            }
            Text {

                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.1
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: devWorry.right
                anchors.leftMargin: parent.width*0.1
                color: "#09BB07"
                text: qsTr("因为网络或商品原因，设备暂时无法使用。")
                font.family: siyuanhei.name
                font.pointSize: 20
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
            }

        }

        Rectangle{
            id:tooMuchCommity
            anchors.centerIn: parent
            width: 1
            height: 1
            Behavior on width {PropertyAnimation { easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
            Behavior on height {PropertyAnimation {easing.overshoot: 1; easing.type: Easing.OutBack;duration: 500} }
            radius:10

            color: "#ffffff"
            visible: false
            onVisibleChanged: {
                if(visible==false){
                    width= 1
                    height= 1
                }else{
                    tei.visible = false
                    width= parent.width*0.4
                    height=parent.height*0.15
                    tei.visible = true
                }
            }

            Image {
                id:mWorry
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.1
                anchors.verticalCenter: parent.verticalCenter
                source: "../Images/worring_w.png"
                height: window.height*0.08
                width: height
            }
            Text {
                id:tei
                anchors.right: parent.right
                anchors.rightMargin: parent.width*0.1
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: mWorry.right
                anchors.leftMargin: parent.width*0.1
                color: "#09BB07"
                text: qsTr("结账台每次结账最多放入4件商品，\n超过数量请分多次结账")
                font.family: siyuanhei.name
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 20
                verticalAlignment: Text.AlignVCenter
            }

        }
    }

    MouseArea{
        anchors.fill: parent
        anchors.topMargin: parent.height*0.8
        //preventStealing:false
        property int i: 0
        onClicked: {
            //settle.visible = true
            //toIdentifing()

                if(i==0){
                    toIdentifing()
                }
                if(i==1){
                    toSettlementView()
                }
                if(i==2){
                   // showFaceCantIdentify()
                    showError(0)
                   //toPaying()
                }
                if(i==3){
                    showError(1)
                  // toRegisterView()
                   //toPaySuccess()
                }
                if(i==4){
                    showError(2)
                   toLeaveStore()
                }
                if(i==5){
                    toWelComeView()
                    i=-1
                }
                i+=1
            }
        }


}
