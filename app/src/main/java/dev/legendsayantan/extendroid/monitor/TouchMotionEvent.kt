package dev.legendsayantan.extendroid.monitor

import android.view.MotionEvent

/**
 * @author legendsayantan
 */
data class TouchMotionEvent(val downTime:Long, val eventTime:Long,val action:Int,val x:Float,val y:Float){

    companion object{
        fun MotionEvent.asTouchEvent(scale:Float=1f,offset:Pair<Float,Float> = Pair(0f,0f)): TouchMotionEvent {
            return TouchMotionEvent(downTime,eventTime,action,(x-offset.first)*scale,(y-offset.second)*scale)
        }
        fun TouchMotionEvent.asMotionEvent(): MotionEvent {
            return MotionEvent.obtain(downTime,eventTime,action,x,y,0)
        }
    }
}