package app.orbit.dial

import android.app.Activity
import android.app.AlertDialog
import android.app.KeyguardManager
import android.os.Build
import android.os.Bundle
import android.view.MotionEvent
import android.view.WindowManager
import app.orbit.dial.core.DialEvent
import app.orbit.dial.core.Kind

/**
 * Press-and-hold arrives as VOICE_COMMAND (the buds send HFP AT+BVRA=1 and the
 * Bluetooth stack starts this intent). An exported activity cannot authenticate
 * that origin on every supported Android version, so ask for a physical confirmation.
 * We deliberately don't call BluetoothHeadset.startVoiceRecognition: that would
 * open a call-quality audio link and pause music; the stack just times out.
 */
class HoldTrampolineActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Orbit.enabled(this) || getSystemService(KeyguardManager::class.java).isKeyguardLocked) {
            finish()
            return
        }
        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
        if (Build.VERSION.SDK_INT >= 31) window.setHideOverlayWindows(true)
        val dialog = AlertDialog.Builder(this)
            .setTitle("Use Orbit hold action?")
            .setMessage("Confirm to run your configured press-and-hold action.")
            .setPositiveButton("Run action") { _, _ ->
                if (!getSystemService(KeyguardManager::class.java).isKeyguardLocked) {
                    Orbit.emit(this, DialEvent(Kind.HOLD, 0, "confirmed-hold"))
                }
                finish()
            }
            .setNegativeButton("Cancel") { _, _ -> finish() }
            .setOnCancelListener { finish() }
            .create()
        dialog.setOnShowListener {
            val confirm = dialog.getButton(AlertDialog.BUTTON_POSITIVE)
            confirm.filterTouchesWhenObscured = true
            confirm.setOnTouchListener { _, event ->
                event.flags and (MotionEvent.FLAG_WINDOW_IS_OBSCURED or MotionEvent.FLAG_WINDOW_IS_PARTIALLY_OBSCURED) != 0
            }
        }
        dialog.show()
    }
}
