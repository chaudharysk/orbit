package app.orbit.dial

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService

/** "Turn off" on the ongoing notification. */
class OrbitToggleReceiver : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        if (i.action == OFF) Orbit.setEnabled(c, false)
    }

    companion object { const val OFF = "app.orbit.dial.OFF" }
}

/** Quick Settings tile: Orbit on / off from the notification shade. */
class OrbitTileService : TileService() {
    override fun onStartListening() = render()

    override fun onClick() {
        Orbit.setEnabled(this, !Orbit.enabled(this))
        render()
    }

    private fun render() {
        val t = qsTile ?: return
        val on = Orbit.enabled(this)
        t.state = if (on) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
        t.label = "Orbit"
        if (android.os.Build.VERSION.SDK_INT >= 29) t.subtitle = if (on) "On" else "Off"
        t.updateTile()
    }
}
