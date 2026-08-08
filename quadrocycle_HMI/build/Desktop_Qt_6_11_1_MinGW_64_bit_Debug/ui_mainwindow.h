/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.11.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QLabel>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPlainTextEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QPlainTextEdit *ConsoleOutput;
    QLabel *ConsoleOutp_lbl;
    QPushButton *ClearConsole_btt;
    QWidget *widget;
    QVBoxLayout *verticalLayout;
    QCheckBox *OUTP1_bx;
    QCheckBox *OUTP2_bx;
    QCheckBox *OUTP3_bx;
    QCheckBox *OUTP10_bx;
    QWidget *widget1;
    QVBoxLayout *verticalLayout_2;
    QCheckBox *OUTP4_bx;
    QCheckBox *OUTP5_bx;
    QCheckBox *OUTP6_bx;
    QWidget *widget2;
    QVBoxLayout *verticalLayout_4;
    QLabel *AnalogVal_lbl;
    QSpinBox *AnalogVal_bx;
    QPushButton *TX_btt;
    QWidget *widget3;
    QVBoxLayout *verticalLayout_3;
    QCheckBox *OUTP7_bx;
    QCheckBox *OUTP8_bx;
    QCheckBox *OUTP9_bx;
    QWidget *widget4;
    QVBoxLayout *verticalLayout_5;
    QRadioButton *CCW_s;
    QRadioButton *CC_s;
    QWidget *widget5;
    QVBoxLayout *verticalLayout_6;
    QRadioButton *BIDir_s;
    QRadioButton *UNIDir_s;
    QWidget *widget6;
    QVBoxLayout *verticalLayout_8;
    QVBoxLayout *verticalLayout_7;
    QLabel *RPM_lbl;
    QSpinBox *RPM_val_;
    QLabel *Angle_lbl;
    QSpinBox *Angle_val_;
    QPushButton *pushButton;
    QButtonGroup *buttonGroup;
    QButtonGroup *buttonGroup_2;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName("MainWindow");
        MainWindow->resize(881, 600);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName("centralwidget");
        ConsoleOutput = new QPlainTextEdit(centralwidget);
        ConsoleOutput->setObjectName("ConsoleOutput");
        ConsoleOutput->setGeometry(QRect(70, 400, 351, 131));
        ConsoleOutput->setReadOnly(true);
        ConsoleOutp_lbl = new QLabel(centralwidget);
        ConsoleOutp_lbl->setObjectName("ConsoleOutp_lbl");
        ConsoleOutp_lbl->setGeometry(QRect(80, 360, 131, 20));
        ClearConsole_btt = new QPushButton(centralwidget);
        ClearConsole_btt->setObjectName("ClearConsole_btt");
        ClearConsole_btt->setGeometry(QRect(430, 400, 61, 51));
        widget = new QWidget(centralwidget);
        widget->setObjectName("widget");
        widget->setGeometry(QRect(80, 110, 83, 123));
        verticalLayout = new QVBoxLayout(widget);
        verticalLayout->setObjectName("verticalLayout");
        verticalLayout->setContentsMargins(0, 0, 0, 0);
        OUTP1_bx = new QCheckBox(widget);
        OUTP1_bx->setObjectName("OUTP1_bx");

        verticalLayout->addWidget(OUTP1_bx);

        OUTP2_bx = new QCheckBox(widget);
        OUTP2_bx->setObjectName("OUTP2_bx");

        verticalLayout->addWidget(OUTP2_bx);

        OUTP3_bx = new QCheckBox(widget);
        OUTP3_bx->setObjectName("OUTP3_bx");

        verticalLayout->addWidget(OUTP3_bx);

        OUTP10_bx = new QCheckBox(widget);
        OUTP10_bx->setObjectName("OUTP10_bx");

        verticalLayout->addWidget(OUTP10_bx);

        widget1 = new QWidget(centralwidget);
        widget1->setObjectName("widget1");
        widget1->setGeometry(QRect(220, 110, 75, 91));
        verticalLayout_2 = new QVBoxLayout(widget1);
        verticalLayout_2->setObjectName("verticalLayout_2");
        verticalLayout_2->setContentsMargins(0, 0, 0, 0);
        OUTP4_bx = new QCheckBox(widget1);
        OUTP4_bx->setObjectName("OUTP4_bx");

        verticalLayout_2->addWidget(OUTP4_bx);

        OUTP5_bx = new QCheckBox(widget1);
        OUTP5_bx->setObjectName("OUTP5_bx");

        verticalLayout_2->addWidget(OUTP5_bx);

        OUTP6_bx = new QCheckBox(widget1);
        OUTP6_bx->setObjectName("OUTP6_bx");

        verticalLayout_2->addWidget(OUTP6_bx);

        widget2 = new QWidget(centralwidget);
        widget2->setObjectName("widget2");
        widget2->setGeometry(QRect(460, 110, 90, 94));
        verticalLayout_4 = new QVBoxLayout(widget2);
        verticalLayout_4->setObjectName("verticalLayout_4");
        verticalLayout_4->setContentsMargins(0, 0, 0, 0);
        AnalogVal_lbl = new QLabel(widget2);
        AnalogVal_lbl->setObjectName("AnalogVal_lbl");

        verticalLayout_4->addWidget(AnalogVal_lbl);

        AnalogVal_bx = new QSpinBox(widget2);
        AnalogVal_bx->setObjectName("AnalogVal_bx");
        AnalogVal_bx->setMaximum(4095);
        AnalogVal_bx->setValue(2048);

        verticalLayout_4->addWidget(AnalogVal_bx);

        TX_btt = new QPushButton(widget2);
        TX_btt->setObjectName("TX_btt");

        verticalLayout_4->addWidget(TX_btt);

        widget3 = new QWidget(centralwidget);
        widget3->setObjectName("widget3");
        widget3->setGeometry(QRect(350, 110, 75, 91));
        verticalLayout_3 = new QVBoxLayout(widget3);
        verticalLayout_3->setObjectName("verticalLayout_3");
        verticalLayout_3->setContentsMargins(0, 0, 0, 0);
        OUTP7_bx = new QCheckBox(widget3);
        OUTP7_bx->setObjectName("OUTP7_bx");

        verticalLayout_3->addWidget(OUTP7_bx);

        OUTP8_bx = new QCheckBox(widget3);
        OUTP8_bx->setObjectName("OUTP8_bx");

        verticalLayout_3->addWidget(OUTP8_bx);

        OUTP9_bx = new QCheckBox(widget3);
        OUTP9_bx->setObjectName("OUTP9_bx");

        verticalLayout_3->addWidget(OUTP9_bx);

        widget4 = new QWidget(centralwidget);
        widget4->setObjectName("widget4");
        widget4->setGeometry(QRect(610, 130, 62, 59));
        verticalLayout_5 = new QVBoxLayout(widget4);
        verticalLayout_5->setObjectName("verticalLayout_5");
        verticalLayout_5->setContentsMargins(0, 0, 0, 0);
        CCW_s = new QRadioButton(widget4);
        buttonGroup = new QButtonGroup(MainWindow);
        buttonGroup->setObjectName("buttonGroup");
        buttonGroup->addButton(CCW_s);
        CCW_s->setObjectName("CCW_s");

        verticalLayout_5->addWidget(CCW_s);

        CC_s = new QRadioButton(widget4);
        buttonGroup->addButton(CC_s);
        CC_s->setObjectName("CC_s");
        CC_s->setChecked(true);

        verticalLayout_5->addWidget(CC_s);

        widget5 = new QWidget(centralwidget);
        widget5->setObjectName("widget5");
        widget5->setGeometry(QRect(690, 130, 130, 59));
        verticalLayout_6 = new QVBoxLayout(widget5);
        verticalLayout_6->setObjectName("verticalLayout_6");
        verticalLayout_6->setContentsMargins(0, 0, 0, 0);
        BIDir_s = new QRadioButton(widget5);
        buttonGroup_2 = new QButtonGroup(MainWindow);
        buttonGroup_2->setObjectName("buttonGroup_2");
        buttonGroup_2->addButton(BIDir_s);
        BIDir_s->setObjectName("BIDir_s");

        verticalLayout_6->addWidget(BIDir_s);

        UNIDir_s = new QRadioButton(widget5);
        buttonGroup_2->addButton(UNIDir_s);
        UNIDir_s->setObjectName("UNIDir_s");
        UNIDir_s->setChecked(true);

        verticalLayout_6->addWidget(UNIDir_s);

        widget6 = new QWidget(centralwidget);
        widget6->setObjectName("widget6");
        widget6->setGeometry(QRect(650, 210, 82, 159));
        verticalLayout_8 = new QVBoxLayout(widget6);
        verticalLayout_8->setObjectName("verticalLayout_8");
        verticalLayout_8->setContentsMargins(0, 0, 0, 0);
        verticalLayout_7 = new QVBoxLayout();
        verticalLayout_7->setObjectName("verticalLayout_7");
        RPM_lbl = new QLabel(widget6);
        RPM_lbl->setObjectName("RPM_lbl");

        verticalLayout_7->addWidget(RPM_lbl);

        RPM_val_ = new QSpinBox(widget6);
        RPM_val_->setObjectName("RPM_val_");
        RPM_val_->setMaximum(120);
        RPM_val_->setValue(60);

        verticalLayout_7->addWidget(RPM_val_);

        Angle_lbl = new QLabel(widget6);
        Angle_lbl->setObjectName("Angle_lbl");

        verticalLayout_7->addWidget(Angle_lbl);

        Angle_val_ = new QSpinBox(widget6);
        Angle_val_->setObjectName("Angle_val_");
        Angle_val_->setMaximum(360);
        Angle_val_->setValue(360);

        verticalLayout_7->addWidget(Angle_val_);


        verticalLayout_8->addLayout(verticalLayout_7);

        pushButton = new QPushButton(widget6);
        pushButton->setObjectName("pushButton");

        verticalLayout_8->addWidget(pushButton);

        MainWindow->setCentralWidget(centralwidget);

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "MainWindow", nullptr));
        ConsoleOutp_lbl->setText(QCoreApplication::translate("MainWindow", "Console Output", nullptr));
        ClearConsole_btt->setText(QCoreApplication::translate("MainWindow", "Clear", nullptr));
        OUTP1_bx->setText(QCoreApplication::translate("MainWindow", "OUTP1", nullptr));
        OUTP2_bx->setText(QCoreApplication::translate("MainWindow", "OUTP2", nullptr));
        OUTP3_bx->setText(QCoreApplication::translate("MainWindow", "OUTP3", nullptr));
        OUTP10_bx->setText(QCoreApplication::translate("MainWindow", "OUTP10", nullptr));
        OUTP4_bx->setText(QCoreApplication::translate("MainWindow", "OUTP4", nullptr));
        OUTP5_bx->setText(QCoreApplication::translate("MainWindow", "OUTP5", nullptr));
        OUTP6_bx->setText(QCoreApplication::translate("MainWindow", "OUTP6", nullptr));
        AnalogVal_lbl->setText(QCoreApplication::translate("MainWindow", "Analog Value", nullptr));
        TX_btt->setText(QCoreApplication::translate("MainWindow", "Transmit", nullptr));
        OUTP7_bx->setText(QCoreApplication::translate("MainWindow", "OUTP7", nullptr));
        OUTP8_bx->setText(QCoreApplication::translate("MainWindow", "OUTP8", nullptr));
        OUTP9_bx->setText(QCoreApplication::translate("MainWindow", "OUTP9", nullptr));
        CCW_s->setText(QCoreApplication::translate("MainWindow", "CCW", nullptr));
        CC_s->setText(QCoreApplication::translate("MainWindow", "CC", nullptr));
        BIDir_s->setText(QCoreApplication::translate("MainWindow", "Return 2 Origin", nullptr));
        UNIDir_s->setText(QCoreApplication::translate("MainWindow", "Unidirectional", nullptr));
        RPM_lbl->setText(QCoreApplication::translate("MainWindow", "RPM", nullptr));
        Angle_lbl->setText(QCoreApplication::translate("MainWindow", "Angle", nullptr));
        pushButton->setText(QCoreApplication::translate("MainWindow", "Transmit", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
