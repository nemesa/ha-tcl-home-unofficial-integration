# ha-tcl-home-unofficial-integration  
**TCL Home Home Assistant integration (unofficial)**

## Known issues
- No branding icons or logos  
- Connection lost after a few hours (maybe fixed, still testing) 

## Supported device types
- Split AC  

## Credit  
The idea for basic login is from [DavidIlie’s project](https://github.com/DavidIlie/tcl-home-ac).  
The Home Assistant integration [samples](https://github.com/msp1974/HAIntegrationExamples) helped a lot.

## How it works  
This integration is the result of reverse-engineering the “TCL Home” Android app. For setup, we only need the username/password used for the app. Since this is not an official integration from TCL, I recommend creating a new user for this integration and sharing your devices with that user—just in case TCL decides to ban the account.

## How to install  
This may eventually become available in the [HACS](https://www.home-assistant.io/integrations), but for now installation is manual only.

### Steps:
1. Download the ZIP from GitHub and extract `ha-tcl-home-unofficial-integration-main.zip`.  
2. Create a folder named `custom_components` next to your `configuration.yaml` (if you don't already have one).  
3. Inside `custom_components`, create a folder named `tcl_home_unofficial`.  
4. Copy all files from the ZIP’s `/ha-tcl-home-unofficial-integration-main/src/tcl_home_unofficial/` folder into your new `custom_components/tcl_home_unofficial` folder.  
5. Restart Home Assistant.  
6. In the UI go to **Settings → Devices & Services → + Add Integration**, then search for “TCL Home” and follow the setup steps.

---

Optionally, you can install the File Editor add-on to upload files and edit `configuration.yaml` via:  
**Settings → Add-ons**, then search for “File editor.”

## Logs
For info logs extend the `configuration.yaml` with
   ```yaml
    logger:
      logs:
        custom_components.tcl_home_unofficial: info
   ```  

## How the integration looks

Dashboard example:  
![Dashboard example](./dashboard_example.jpg "Dashboard example")

Integration mapping to the app:  
![Integration mapping to the app](./integration_map_to_app.jpg "Integration mapping to the app")