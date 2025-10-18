#!/usr/bin/env python3
# main.py — Generator + Android Studio CLI Builder
# Usage:
#   python3 main.py --main ./app.py --pydroid ./pydroid3.apk --package com.byby.tkhost --appname BybyTkHost

import os, shutil, argparse, subprocess, sys

# ----------------------------
# Template (escaped cho an toàn)
# ----------------------------

TEMPLATE_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest package="{package}" xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>

    <application
        android:allowBackup="true"
        android:label="{appname}"
        android:icon="@android:drawable/sym_def_app_icon">
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="{package}.provider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>

        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

TEMPLATE_FILE_PATHS = """<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <files-path name="files" path="."/>
    <external-files-path name="ext_files" path="."/>
</paths>
"""

# escape toàn bộ { } trong code gradle để format không hiểu nhầm
TEMPLATE_BUILD_GRADLE_ROOT = """buildscript {{
    repositories {{ google(); mavenCentral() }}
    dependencies {{ classpath 'com.android.tools.build:gradle:8.5.0' }}
}}
allprojects {{
    repositories {{ google(); mavenCentral() }}
}}
"""

TEMPLATE_SETTINGS_GRADLE = """pluginManagement {{
    repositories {{ google(); gradlePluginPortal(); mavenCentral() }}
}}
rootProject.name = "{appname}"
include ':app'
"""

TEMPLATE_APP_BUILD_GRADLE = """apply plugin: 'com.android.application'

android {{
    namespace "{package}"
    compileSdk 34

    defaultConfig {{
        applicationId "{package}"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.core:core-ktx:1.9.0'
}}
"""

TEMPLATE_MAIN_ACTIVITY = """package {package};
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.FileProvider;
import android.widget.Toast;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.IOException;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Thông báo duy nhất
        Toast.makeText(this, "App này cần cài Pydroid 3.", Toast.LENGTH_LONG).show();

        // Copy main.py (nếu lỗi, ném RuntimeException → crash app)
        File script = new File(getExternalFilesDir(null), "main.py");
        InputStream in;
        FileOutputStream fo;
        try {
            in = getAssets().open("main.py");
            fo = new FileOutputStream(script);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        try {
            byte[] buf = new byte[4096];
            int len;
            while ((len = in.read(buf)) > 0) {
                fo.write(buf, 0, len);
            }
            fo.flush();
            fo.close();
            in.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        // Start intent chạy Python, crash nếu không có app nhận
        Intent runIntent = new Intent(Intent.ACTION_VIEW);
        Uri scriptUri = FileProvider.getUriForFile(this, getPackageName() + ".provider", script);
        runIntent.setDataAndType(scriptUri, "text/x-python");
        runIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(runIntent);
    }
}
"""

# ----------------------------
# Hàm tiện ích
# ----------------------------

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

# ----------------------------
# Main logic
# ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--pydroid", required=True)
    ap.add_argument("--package", required=True)
    ap.add_argument("--appname", required=True)
    ap.add_argument("--out", default="android_host_project")
    args = ap.parse_args()

    if not os.path.exists(args.main):
        print("❌ main.py not found"); sys.exit(1)
    if not os.path.exists(args.pydroid):
        print("❌ pydroid3.apk not found"); sys.exit(1)

    out = args.out
    app_dir = os.path.join(out, "app")
    java_dir = os.path.join(app_dir, "src", "main", "java", *args.package.split("."))
    assets_dir = os.path.join(app_dir, "src", "main", "assets")
    res_xml_dir = os.path.join(app_dir, "src", "main", "res", "xml")
    res_values_dir = os.path.join(app_dir, "src", "main", "res", "values")

    os.makedirs(java_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(res_xml_dir, exist_ok=True)
    os.makedirs(res_values_dir, exist_ok=True)

    # Viết file project
    write_file(os.path.join(out, "build.gradle"), TEMPLATE_BUILD_GRADLE_ROOT)
    write_file(os.path.join(out, "settings.gradle"), TEMPLATE_SETTINGS_GRADLE.format(appname=args.appname))
    write_file(os.path.join(app_dir, "build.gradle"), TEMPLATE_APP_BUILD_GRADLE.format(package=args.package))
    write_file(os.path.join(app_dir, "src", "main", "AndroidManifest.xml"),
               TEMPLATE_MANIFEST.format(package=args.package, appname=args.appname))
    write_file(os.path.join(res_xml_dir, "file_paths.xml"), TEMPLATE_FILE_PATHS)
    write_file(os.path.join(res_values_dir, "strings.xml"),
               f"<resources><string name='app_name'>{args.appname}</string></resources>")
    write_file(os.path.join(java_dir, "MainActivity.java"),
               TEMPLATE_MAIN_ACTIVITY.format(package=args.package))
    copy_file(args.main, os.path.join(assets_dir, "main.py"))
    copy_file(args.pydroid, os.path.join(assets_dir, "pydroid3.apk"))
    with open("gradle.properties", "w", encoding="utf-8") as f:
        f.write("android.useAndroidX=true\n")
        f.write("android.enableJetifier=true\n")

    print(f"✅ Project generated successfully at: {out}")

    # ----------------------------
    # Build bằng Android Studio CLI
    # ----------------------------
    print("⚙️  Building APK using Android Studio CLI...")
    try:
        subprocess.run(["studio", "build", out], check=True)
        print("✅ Build completed successfully via Android Studio CLI.")
    except FileNotFoundError:
        print("❌ Error: 'studio' CLI not found in PATH.")
    except subprocess.CalledProcessError as e:
        print("❌ Build failed:", e)

if __name__ == "__main__":
    main()
