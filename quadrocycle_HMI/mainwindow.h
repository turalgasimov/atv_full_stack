#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "QSerialPort"
#include "QSerialPortInfo"
#include "QDebug"


QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

private slots:
    void on_ClearConsole_btt_clicked();
    void portRXappendConsole();
    void on_TX_btt_clicked();

    void on_pushButton_clicked();

private:
    QSerialPort *serialport = NULL;
    Ui::MainWindow *ui;
    bool is_serialport_open = false;
    bool console_mutex_capture = false;
    uint16_t calculate_modbus_crc(uint8_t *buffer, int length);
};
#endif // MAINWINDOW_H
