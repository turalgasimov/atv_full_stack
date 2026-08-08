package com.example.atv_rc

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.InputDevice
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import org.json.JSONObject
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread
import kotlin.math.abs

class MainActivity : AppCompatActivity() {

    // UPDATE THIS to Jetson's Wi-Fi IP address
    private val jetsonIp = "10.121.0.158"
    private val jetsonPort = 5005
    private var udpSocket: DatagramSocket? = null
    private var jetsonAddress: InetAddress? = null
    private var executor: ScheduledExecutorService? = null

    // UI Elements
    private lateinit var gearR: TextView
    private lateinit var gearD: TextView
    private lateinit var motorLight: View
    private lateinit var safetyStatusText: TextView
    private lateinit var xValueText: TextView
    private lateinit var yValueText: TextView

    // Control State - Volatile for thread safety with the 10ms executor
    @Volatile private var motorOn = 0 // 0: Off, 1: On
    @Volatile private var isReady = false // Safety protocol
    @Volatile private var direction = "R" // Default Reverse
    @Volatile private var currentX = 0.0f
    @Volatile private var currentY = 0.0f
    @Volatile private var mappedY = 0 // Neutral at 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI
        gearR = findViewById(R.id.gearR)
        gearD = findViewById(R.id.gearD)
        motorLight = findViewById(R.id.motorLight)
        safetyStatusText = findViewById(R.id.safetyStatusText)
        xValueText = findViewById(R.id.xValueText)
        yValueText = findViewById(R.id.yValueText)

        updateUI()

        // Initialize socket and pre-resolve address on a background thread
        thread {
            try {
                udpSocket = DatagramSocket()
                jetsonAddress = InetAddress.getByName(jetsonIp)
                
                // Start the 10ms periodic transmission
                startTransmissionLoop()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun startTransmissionLoop() {
        executor = Executors.newSingleThreadScheduledExecutor()
        executor?.scheduleWithFixedDelay({
            sendDataInternal()
        }, 0, 20, TimeUnit.MILLISECONDS)
    }

    override fun onGenericMotionEvent(event: MotionEvent): Boolean {
        if (event.isFromSource(InputDevice.SOURCE_JOYSTICK) && event.action == MotionEvent.ACTION_MOVE) {
            if (motorOn == 1) {
                currentX = event.getAxisValue(MotionEvent.AXIS_X)
                currentY = event.getAxisValue(MotionEvent.AXIS_Y)
                mappedY = if (currentY <= 0f) {
                    (abs(currentY) * 4095).toInt()
                } else {
                    0 
                }
            } else {
                currentX = 0.0f
                currentY = 0.0f
                mappedY = 0
            }

            updateUI()
            // No longer calling sendData() here; loop handles it
            return true
        }
        return super.onGenericMotionEvent(event)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        if (event.repeatCount > 0) return super.onKeyDown(keyCode, event)

        var handled = false
        when (keyCode) {
            KeyEvent.KEYCODE_BUTTON_Z -> { // 101 - Motor Latch
                motorOn = 1
                handled = true
            }
            KeyEvent.KEYCODE_BUTTON_L1 -> { // 102 - Gear Shift
                if (motorOn == 1) {
                    direction = "D"
                    handled = true
                }
            }
            KeyEvent.KEYCODE_BUTTON_A -> { // 96 - Safety Toggle
                if (motorOn == 1) {
                    isReady = !isReady
                    handled = true
                }
            }
        }
        if (handled) {
            updateUI()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onKeyUp(keyCode: Int, event: KeyEvent): Boolean {
        var handled = false
        when (keyCode) {
            KeyEvent.KEYCODE_BUTTON_Z -> { // 101 - Motor OFF
                motorOn = 0
                isReady = false 
                currentX = 0.0f
                currentY = 0.0f
                mappedY = 0
                handled = true
            }
            KeyEvent.KEYCODE_BUTTON_L1 -> { // 102 - Return to Reverse
                direction = "R"
                handled = true
            }
        }

        if (handled) {
            updateUI()
            return true
        }
        return super.onKeyUp(keyCode, event)
    }

    @SuppressLint("SetTextI18n")
    private fun updateUI() {
        runOnUiThread {
            val isEnabled = motorOn == 1

            if (isEnabled) {
                if (direction == "D") {
                    gearD.setBackgroundColor(ContextCompat.getColor(this, R.color.status_green))
                    gearD.setTextColor(ContextCompat.getColor(this, R.color.white))
                    gearR.setBackgroundResource(0)
                    gearR.setTextColor(ContextCompat.getColor(this, R.color.gear_inactive))
                } else {
                    gearR.setBackgroundColor(ContextCompat.getColor(this, R.color.status_red))
                    gearR.setTextColor(ContextCompat.getColor(this, R.color.white))
                    gearD.setBackgroundResource(0)
                    gearD.setTextColor(ContextCompat.getColor(this, R.color.gear_inactive))
                }
            } else {
                gearR.setBackgroundResource(0)
                gearD.setBackgroundResource(0)
                gearR.setTextColor(ContextCompat.getColor(this, R.color.gear_inactive))
                gearD.setTextColor(ContextCompat.getColor(this, R.color.gear_inactive))
            }

            if (isEnabled) {
                motorLight.alpha = 1.0f
                motorLight.setBackgroundColor(ContextCompat.getColor(this, R.color.bright_red))
            } else {
                motorLight.alpha = 0.1f
                motorLight.setBackgroundColor(ContextCompat.getColor(this, R.color.gear_inactive))
            }

            if (isEnabled) {
                if (isReady) {
                    safetyStatusText.text = "READY"
                    safetyStatusText.setTextColor(ContextCompat.getColor(this, R.color.status_green))
                } else {
                    safetyStatusText.text = "LOCKED"
                    safetyStatusText.setTextColor(ContextCompat.getColor(this, R.color.status_red))
                }
            } else {
                safetyStatusText.text = "OFF"
                safetyStatusText.setTextColor(ContextCompat.getColor(this, R.color.gear_inactive))
            }
            
            xValueText.text = "X: %.2f".format(currentX)
            yValueText.text = "Y: $mappedY"
        }
    }

    private fun sendDataInternal() {
        try {
            val address = jetsonAddress ?: return
            val socket = udpSocket ?: return

            val json = JSONObject()
            json.put("motor_on", motorOn)
            json.put("direction", direction)
            json.put("ready", isReady)

            if (motorOn == 1 && isReady) {
                json.put("x", currentX)
                json.put("y", mappedY)
            } else {
                json.put("x", 0.0)
                json.put("y", 0)
            }

            val message = json.toString().toByteArray()
            val packet = DatagramPacket(message, message.size, address, jetsonPort)
            socket.send(packet)
        } catch (e: Exception) {
            // Avoid logging every 10ms to keep logcat clean; maybe log once or on state change
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor?.shutdown()
        udpSocket?.close()
    }
}