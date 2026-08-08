#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    serialport = new QSerialPort(this);
    serialport->setBaudRate(QSerialPort::Baud38400);
    serialport->setDataBits(QSerialPort::Data8);
    serialport->setStopBits(QSerialPort::OneStop);
    serialport->setParity(QSerialPort::NoParity);
    serialport->setFlowControl(QSerialPort::NoFlowControl);
    auto portinfos = QSerialPortInfo::availablePorts();
    connect(serialport,&QSerialPort::readyRead,this,&MainWindow::portRXappendConsole);
    // for (QSerialPortInfo &info:portinfos) {
    //     if(info.portName()!=""){
            // serialport->setPortName(info.portName());
    serialport->setPortName("COM3");
            is_serialport_open = serialport->open(QIODevice::ReadWrite);
            qDebug()<<"Serial port status is "<<((is_serialport_open==true)?"open":"closed")<<"\r\n";
            if(is_serialport_open==true){
                serialport->setBreakEnabled(false);
                // qDebug()<<"Serial port name is "<<info.portName()<<"\r\n";
                uint8_t txd[8] = {0x01,0x03,0x00,0xfd,0x00,0x01,0x15,0xfa};
                serialport->write((char*)txd,8);
                serialport->flush();
                serialport->waitForBytesWritten(100);
                serialport->waitForReadyRead(100);
                qDebug()<<serialport->readAll().toHex(' ')<<"\r\n";
            }
    //         break;
    //     }
    // }
    if(serialport->portName() == "") qDebug()<<"No serial port is detected\r\n";
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_ClearConsole_btt_clicked()
{
    if(console_mutex_capture == false) ui->ConsoleOutput->clear();
}

void MainWindow::portRXappendConsole(){
    console_mutex_capture = true;
    // ui->ConsoleOutput->appendPlainText(serialport->readAll()/*.toHex(' ')*/);
    qDebug()<<serialport->readAll()<<"\r\n";
    console_mutex_capture = false;
}

uint16_t MainWindow::calculate_modbus_crc(uint8_t *buffer, int length) {
    uint16_t crc = 0xFFFF; // Step 1

    for (int i = 0; i < length; i++) {
        crc ^= (uint16_t)buffer[i]; // Step 2

        for (int j = 8; j != 0; j--) { // Step 3 & 4
            if ((crc & 0x0001) != 0) {
                crc >>= 1;
                crc ^= 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

void MainWindow::on_TX_btt_clicked()
{
    QByteArray tx = {};
    tx.append("{\"MSGshort\":0,");
    tx.append("\"LOG\":1,");
    tx.append("\"PrintLastLog\":0,");
    tx.append("\"SysPWDN\":0,");
    tx.append("\"MotorPWDN\":0,");

    tx.append("\"PBTT0\":");
    if(ui->OUTP1_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT1\":");
    if(ui->OUTP2_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT2\":");
    if(ui->OUTP3_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT3\":");
    if(ui->OUTP4_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT4\":");
    if(ui->OUTP5_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT5\":");
    if(ui->OUTP6_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT6\":");
    if(ui->OUTP7_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT7\":");
    if(ui->OUTP8_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT8\":");
    if(ui->OUTP9_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"PBTT9\":");
    if(ui->OUTP10_bx->isChecked()) tx.append("1,");
    else tx.append("0,");

    tx.append("\"HBTT\":");
    tx.append(QByteArray::number(ui->AnalogVal_bx->value()));
    tx.append("}");
    uint16_t size = tx.size();

    uint16_t CRC_ = calculate_modbus_crc((uint8_t*)tx.data(),size);
    qDebug()<<"CRC value is:"<<Qt::hex<<(CRC_)<<"\r\n";
    tx.append(":");
    tx.append(QByteArray::number((uint8_t)(CRC_&0xFF),16).rightJustified(2, '0').toUpper());
    tx.append(QByteArray::number((uint8_t)(CRC_>>8),16).rightJustified(2, '0').toUpper());
    console_mutex_capture = true;
    ui->ConsoleOutput->appendPlainText("\r\n");
    ui->ConsoleOutput->appendPlainText(tx.data());
    serialport->write(tx.data());
    console_mutex_capture = false;

}


void MainWindow::on_pushButton_clicked()
{
    QByteArray tx = {};
    uint8_t ccwbackhome = 0;
    tx.append("{\"MSGshort\":1,");
    tx.append("\"CCW\":");
    ccwbackhome = (ui->CC_s->isChecked()*1+ui->CCW_s->isChecked()*2) + ui->BIDir_s->isChecked()*2;
    tx.append(QByteArray::number(ccwbackhome)+",");
    tx.append("\"ANG\":");
    tx.append(QByteArray::number(ui->Angle_val_->value())+",");
    tx.append("\"RPM\":");
    tx.append(QByteArray::number(ui->RPM_val_->value())+"}");
    uint16_t size = tx.size();

    uint16_t CRC_ = calculate_modbus_crc((uint8_t*)tx.data(),size);
    qDebug()<<"CRC value is:"<<Qt::hex<<(CRC_)<<"\r\n";
    tx.append(":");
    tx.append(QByteArray::number((uint8_t)(CRC_&0xFF),16).rightJustified(2, '0').toUpper());
    tx.append(QByteArray::number((uint8_t)(CRC_>>8),16).rightJustified(2, '0').toUpper());
    console_mutex_capture = true;
    ui->ConsoleOutput->appendPlainText("\r\n");
    ui->ConsoleOutput->appendPlainText(tx.data());
    serialport->write(tx.data());
    console_mutex_capture = false;
}

