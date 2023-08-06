# Myenergi API

This is a package for connecting to the Myenergi API.

## Usage

```python
import myenergi

def main():
    with myenergi.API(serial="123456", password="passw0rd") as mye:
        print(mye.get_serials(myenergi.const.MyenergiType.ZAPPI))

run(main())
```

The sample programs use a .env file with the serial and password contained in it

```
myenergi_serial = "1234567"
myenergi_password = "passw0rd"
```


