package app.orbit.dial

import android.app.AlertDialog
import android.app.KeyguardManager
import android.content.Context
import android.content.Intent
import android.os.Looper
import app.orbit.dial.core.DialEvent
import app.orbit.dial.core.Kind
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowAlertDialog

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class EntryPointSecurityTest {
    private lateinit var ctx: Context
    private lateinit var collector: Job
    private val events = mutableListOf<DialEvent>()

    @Before fun setup() {
        ctx = RuntimeEnvironment.getApplication()
        Orbit.prefs(ctx).edit().clear().putBoolean("enabled", true).putBoolean("require_bt", true).commit()
        Orbit.a11y = null; Orbit.media = null
        shadowOf(ctx.getSystemService(KeyguardManager::class.java)).setKeyguardLocked(false)
        collector = CoroutineScope(Dispatchers.Unconfined).launch { Orbit.events.collect { events += it } }
    }

    @After fun cleanup() { collector.cancel() }

    @Test fun exportedLauncherIgnoresTestExtrasOnCreateAndNewIntent() {
        val intent = Intent(ctx, MainActivity::class.java).putExtra("emit", "hold").putExtra("require_bt", false)
        val activity = Robolectric.buildActivity(MainActivity::class.java, intent).create()
        activity.newIntent(Intent(intent).putExtra("emit", "double"))
        assertTrue(events.isEmpty())
        assertTrue(Orbit.prefs(ctx).getBoolean("require_bt", false))
        activity.destroy()
    }

    @Test fun externalHoldDoesNotRunUntilTheUserConfirms() {
        val activity = Robolectric.buildActivity(HoldTrampolineActivity::class.java).setup()
        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        assertNotNull(dialog); assertTrue(dialog.isShowing)
        assertTrue(events.isEmpty())
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).performClick()
        shadowOf(Looper.getMainLooper()).idle()
        assertEquals(listOf(Kind.HOLD), events.map { it.kind })
        activity.pause().stop().destroy()
    }

    @Test fun cancellingHoldCannotTriggerAnAction() {
        val activity = Robolectric.buildActivity(HoldTrampolineActivity::class.java).setup()
        ShadowAlertDialog.getLatestAlertDialog().getButton(AlertDialog.BUTTON_NEGATIVE).performClick()
        shadowOf(Looper.getMainLooper()).idle()
        assertTrue(events.isEmpty())
        activity.pause().stop().destroy()
    }

    @Test fun aLockedDeviceRejectsHoldWithoutAnAction() {
        shadowOf(ctx.getSystemService(KeyguardManager::class.java)).setKeyguardLocked(true)
        val activity = Robolectric.buildActivity(HoldTrampolineActivity::class.java).create()
        assertTrue(activity.get().isFinishing)
        assertTrue(events.isEmpty())
        activity.destroy()
    }

    @Test fun turningOffWhileConfirmationIsOpenStillBlocksTheAction() {
        val activity = Robolectric.buildActivity(HoldTrampolineActivity::class.java).setup()
        Orbit.prefs(ctx).edit().putBoolean("enabled", false).commit()
        ShadowAlertDialog.getLatestAlertDialog().getButton(AlertDialog.BUTTON_POSITIVE).performClick()
        shadowOf(Looper.getMainLooper()).idle()
        Orbit.emit(ctx, DialEvent(Kind.DOUBLE, 0, "late-event"))
        assertTrue(events.isEmpty())
        activity.pause().stop().destroy()
    }
}
