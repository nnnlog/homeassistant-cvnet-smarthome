# Homeassistant Integration for CVnet
This is a Home Assistant integration for CVnet. It is designed to work with CVnet SmartHome application.

## Description
You can connect the devices of [CVnet SmartHome application](https://play.google.com/store/apps/details?id=com.cvnet.smarthome.cvnet&hl=ko) into the Homeassistant.

### Integration
You must register the account in the CVnet SmartHome application first. And then, you should enter your account information to the form during setting up integration entry.
![image](https://github.com/user-attachments/assets/36a23794-0720-42e7-b459-73a16a4f8dee)


## Installation
### HACS
With [HACS](https://github.com/hacs/integration), you can install this integration easily:
- Add the custom repository URL `https://github.com/nnnlog/homeassistant-cvnet-smarthome`
- Search for `CVnet SmartHome` in HACS and install it.

### Manual Installation
Copy contents of `custom_components/cvnet/` to your Home Assistant `custom_components/cvnet/` directory.

## Supported Devices
- Heating
- Light
- Ventilator
- Standby Power (Power Outlet)
- Telemetering (Energy, Water, Gas)

## Screenshots
![image](https://github.com/user-attachments/assets/c5091e20-90e0-4985-8724-bae40dff4342)
![image](https://github.com/user-attachments/assets/d8e73655-85e3-4aee-8079-462d7fdc7f42)
![image](https://github.com/user-attachments/assets/34c4bfbc-e148-47b5-bf08-b0f865460012)
