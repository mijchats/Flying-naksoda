[app]
title = Flying Naksoda
package.name = flyingnaksoda
package.domain = org.naksoda

source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,mp3,ogg,ttf

version = 1.0

requirements = python3,pygame

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
