package com.byby.tkhost;

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
