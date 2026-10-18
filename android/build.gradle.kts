// Kotlin 2.4 metadata needs the matching D8/R8 when using AGP 8.x.
buildscript {
    repositories { google(); mavenCentral() }
    dependencies { classpath("com.android.tools:r8:9.1.29") }
}

plugins {
    id("com.android.application") version "8.11.1" apply false
    id("org.jetbrains.kotlin.android") version "2.4.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.4.21" apply false
}
