import argparse
import openrazer.client
from PIL import Image
import os
import subprocess


def resize_image(image:Image,size:tuple[int,int]) -> Image:
        return image.resize(size)

def get_gnome_wallpaper_uri():
    try:
        # Run the gsettings command to get the wallpaper URI
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.background", "picture-uri"],
            capture_output=True,
            text=True
        )

        # Extract the URI from the output
        wallpaper_uri = result.stdout.strip()

        # Remove the single quotes surrounding the URI, if any
        if wallpaper_uri.startswith("'") and wallpaper_uri.endswith("'"):
            wallpaper_uri = wallpaper_uri[1:-1]

        return wallpaper_uri.split("file://")[1]

    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return None


def set_effect(device,resized_image:Image):
    device.fx.advanced.draw()
    for row in range(device.fx.advanced.rows):
        for col in range(device.fx.advanced.cols):
            device.fx.advanced.matrix[row,col] = resized_image.getpixel((col,row))
    device.fx.advanced.draw()


class ListDevices(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        print("\n".join([f"{i}- {device._name}" for i,device in enumerate(devices)]))
        parser.exit()
    

if __name__ == "__main__":
    devman = openrazer.client.DeviceManager()
    devices = devman.devices

    parser = argparse.ArgumentParser(prog = 'ImageToEffect',description = "Configure your Razer device's color to match the specified image.")

    # group1 = parser.add_mutually_exclusive_group()
    parser.add_argument('-l',nargs=0, action=ListDevices,help="List all available devices.")


    parser.add_argument('-i',action='store',required=True,help="Image path for extracting colors, using w will use current wallpaper as image.")
    parser.add_argument('-d',action='store',type=int,required=True,help="Device id for setting colors, using -1 will set all devices.")
    
    args = parser.parse_args()

    if not os.path.isfile(args.i) and args.i != "w":
        raise FileNotFoundError(f"Image file {args.i} was not found.")
    
    if args.i == "w":
        image = Image.open(get_gnome_wallpaper_uri())
    else:
        image = Image.open(args.i)
    
    if args.d == -1:
        for device in devices:
            resized_image =  resize_image(image,(device.fx.advanced.cols,device.fx.advanced.rows))
            set_effect(device,resized_image)
    
    else:
        device = devices[args.d]
        resized_image =  resize_image(image,(device.fx.advanced.cols,device.fx.advanced.rows))
        set_effect(device,resized_image)