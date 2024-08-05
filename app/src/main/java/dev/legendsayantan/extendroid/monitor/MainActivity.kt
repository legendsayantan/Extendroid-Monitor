package dev.legendsayantan.extendroid.monitor

import android.annotation.SuppressLint
import android.graphics.BitmapFactory
import android.os.Bundle
import android.os.Handler
import android.util.Log
import android.view.MotionEvent
import android.widget.EditText
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.gson.Gson
import dev.legendsayantan.extendroid.monitor.TouchMotionEvent.Companion.asTouchEvent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import kotlin.math.max

class MainActivity : AppCompatActivity() {

    private lateinit var imageView: ImageView
    var params : Pair<Int,Int>? = null

    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val socket = DatagramSocket()
        imageView = findViewById(R.id.imageView)
        findViewById<MaterialButton>(R.id.start).setOnClickListener {
            val ip = findViewById<EditText>(R.id.ip).text.toString()
            val port = findViewById<EditText>(R.id.port).text.toString().toInt()
            receiveUdpPackets(socket,ip,port)
            imageView.setOnTouchListener { v, event ->
                val location = intArrayOf(0, 0)
                v.getLocationOnScreen(location)
                sendMotionEvent(socket,ip,port,event,
                    if(params!=null) max(params!!.first.toFloat()/v.width,params!!.second.toFloat()/v.height) else 1f,
                    location[0].toFloat() to location[1].toFloat()
                )
                return@setOnTouchListener true
            }
        }

    }

    private fun receiveUdpPackets(socket:DatagramSocket,ip:String,port:Int) {
        val handler = Handler(mainLooper)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val connection = byteArrayOf(Type.CONNECTION.ordinal.toByte())
                socket.send(DatagramPacket(connection, connection.size,InetAddress.getByName(ip),port))
                val buffer = ByteArray(65507)
                while (true) {
                    val packet = DatagramPacket(buffer, buffer.size)
                    socket.receive(packet)
                    val bitmap = BitmapFactory.decodeByteArray(packet.data, 0, packet.data.size)
                    if(params==null) params = Pair(bitmap.width,bitmap.height)
                    handler.post { imageView.setImageBitmap(bitmap) }
                }
            } catch (e: Exception) {
                Log.e("UDP", "Error receiving UDP packet", e)
            }
        }

    }

    private fun sendMotionEvent(socket: DatagramSocket,ip:String,port:Int,event: MotionEvent,scale:Float,offset:Pair<Float,Float>){
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val connection = Gson().toJson(event.asTouchEvent(scale,offset)).toByteArray()
                println(String(connection))
                val data = ByteArray(connection.size+1)
                data[0] = Type.MOTIONEVENT.ordinal.toByte()
                connection.copyInto(data,1)
                socket.send(DatagramPacket(data, data.size,InetAddress.getByName(ip),port))
            }catch (_:Exception){
                Log.e("UDP", "Error sending UDP packet")
            }
        }
    }
    enum class Type{
        CONNECTION, MOTIONEVENT, KEYEVENT, DISCONNECTION
    }
}