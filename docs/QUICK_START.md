# Travel Memory Map quick start

This guide explains the **current map-and-album prototype**. It is a fictional demo, not yet the final photo-upload and AI-memory application.

## Start the prototype

1. Open PowerShell in the project folder.
2. Run:

   ```powershell
   python serve.py
   ```

3. Open [http://127.0.0.1:8019/app/?map=local](http://127.0.0.1:8019/app/?map=local) in a browser.

No API key, account, photo upload, or npm installation is needed for this demo.

## Try the working sample flow

1. On the map, choose **Osaka** from the city list or its map marker.
2. Confirm that Osaka starts with **2 visits** and two fictional memory cards.
3. Scroll to the bottom of the Osaka panel and open **Try visit counting**.
4. Select **Add a sample visit**. Osaka should now show **3 visits** and a third card.
5. On the new card, select **Edit sample text**, type a short fictional memory, then choose **Save sample text**.
6. Confirm that the text changes while the visit count remains **3**.
7. Reload the page. The third sample card and the count should still be present in the same browser.

Use **Reset sample album** in the footer when you are finished to restore the original fictional records.

## Important current limitation

The current interface does **not** let you create a real memory from your own city, photos, or notes. "Add a sample visit" only creates a fictional record for testing the map. Photo upload, real saved trips, and AI-generated memory drafts are planned work and are not available yet.

Do not enter personal travel notes or upload private photos for this prototype.
