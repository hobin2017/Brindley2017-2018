import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQml 2.2


Rectangle {
    visible: true
    id:wellcomewidows
    color: "#09BB07"
    FontLoader { id: siyuanhei; source: "../font/siyuanheiti.ttf" }
    Text {
        color: "#ffffff"
        anchors.fill: parent
        text: qsTr("请将商品放入识别区")
        font.family: siyuanhei.name
        font.pointSize: 35
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }
    AnimatedImage {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height*0.1
        anchors.horizontalCenter: parent.horizontalCenter
        fillMode: Image.PreserveAspectFit
        height: parent.height*0.10
        source: "../Images/down.gif"
        width: height * 0.4
    }
}


