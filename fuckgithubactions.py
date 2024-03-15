from datetime import datetime

print(type(datetime.now().hour))
print(int(datetime.strptime("16:00:00", "%H:%M:%S").strftime("%H")))

for i in range(10):
    for i in range(5):
        if datetime.now().hour >= int(datetime.strptime("16:00:00", "%H:%M:%S").strftime("%H")):
            print(i)
            continue
    print("testing")
