import os


def delete_pngs():
    dirname = os.path.dirname(os.path.abspath(__file__))
    img_path = dirname + "\\..\\static\\rhythm\\img\\generated"
    test = os.listdir(img_path)

    for item in test:
        if item.endswith(".png"):
            os.remove(os.path.join(img_path, item))


# delete_pngs()
