const serviceUuid = "19b10010-e8f2-537e-4f6c-d104768a1214";
let myCharacteristic;
let myValue = 0;
let myBLE;
let isConnected = false;
let gauge;
let myInterval;
let summer = [0x53];
let winter = [0x57];
let comfortModelType = summer;

function switchComfortType() {
    console.log("Switching comfort model type");
    if (comfortModelType == summer) {
        comfortModelType = winter;
        console.log("Switched to winter");
        alert('Switching to Winter');
    } else {
        comfortModelType = summer;
        console.log("Switched to summer");
        alert('Switching to Summer');
    }
    myBLE.write(myCharacteristic, comfortModelType); //0x53 summer, 0x57 winter
    alert('Switched Comfort Model');
}

function isWinter() {
    document.getElementById("is_winter").style = "display:inline;";
    document.getElementById("is_summer").style = "display:none;";
}

function setLastRead() {
    document.getElementById("lastread").innerHTML = new Date();
}

function setTempHumVals(msg) {
    document.getElementById("tempHumVals").innerHTML = msg;
}

function clearLastRead() {
    document.getElementById("lastread").innerHTML = "No data";
    setGaugeValue(0);
    setTempHumVals("n/a");
}

function isSummer() {
    document.getElementById("is_winter").style = "display:none;";
    document.getElementById("is_summer").style = "display:inline;";
}

function connectingState() {
    console.log("Connecting...");
    document.getElementById("connect_button").classList.add("disabledbutton");
    document.getElementById("connect_button_text").innerHTML = "Connecting...";
}

function disconnectedState() {
    console.log("Disconnected.");
    clearLastRead();
    document.getElementById("connect_button_text").innerHTML = "Connect";
    document.getElementById("connect_button").classList.remove("disabledbutton");
}

function connectedState() {
    console.log("Connected.");
    document.getElementById("connect_button_text").innerHTML = "Disconnect";
    document.getElementById("connect_button").classList.remove("disabledbutton");
}

function onDisconnected() {
    console.log('Device got disconnected.');
    isConnected = false;
    updateStatus();
    // clearInterval(myInterval);
}

function connect(ev) {
    // Process the event
    connectingState();
    if (!isConnected) {
        connectToBle();
        // myInterval = setInterval(function() {
        //     updateStatus();
        // }, 30000);
    } else {
        myBLE.disconnect();
        // clearInterval(myInterval);
        isConnected = myBLE.isConnected();
        updateStatus();
    }
}

function updateStatus() {
    if (isConnected) {
        connectedState();
    } else {
        disconnectedState();
    }
}

function setGaugeValue(value) {
    if (value === undefined) {
        value = 0;
    }

    if (gauge !== undefined) {
        gauge.update(value);
    } else {
        var config1 = liquidFillGaugeDefaultSettings();
        config1.circleThickness = 0.15;
        config1.waveAnimateTime = 1000;
        config1.waveHeight = 0.05;
        config1.waveAnimate = true;
        config1.waveRise = true;
        config1.waveHeightScaling = false;
        config1.waveOffset = 0.25;
        config1.waveCount = 3;
        config1.textVertPosition = 0.52;
        config1.textSize = 1.2;
        config1.displayPercent = false;
        config1.circleColor = "#AFE1AF";
        config1.textColor = "#097969";
        config1.waveTextColor = "#90EE90";
        config1.waveColor = "#228B22";

        gauge = loadLiquidFillGauge("fillgauge1", value, config1);
    }

}

function setup() {
    myBLE = new p5ble();
}

function connectToBle() {
    connectingState();
    // Connect to a device by passing the service UUID
    myBLE.connect(serviceUuid, gotCharacteristics);
    isConnected = myBLE.isConnected();
}

// A function that will be called once got characteristics
function gotCharacteristics(error, characteristics) {
    isConnected = myBLE.isConnected();
    if (isConnected) {
        if (error) console.log('error: ', error);
        console.log('characteristics: ', characteristics);
        if (characteristics != undefined) {
            myCharacteristic = characteristics[0];
            // Read the value of the first characteristic
            // myBLE.read(myCharacteristic, gotValue);
            // Start notifications on the first characteristic by passing the characteristic
            // And a callback function to handle notifications
            myBLE.startNotifications(myCharacteristic, handleNotifications, 'string');
            // You can also pass in the dataType
            // Options: 'unit8', 'uint16', 'uint32', 'int8', 'int16', 'int32', 'float32', 'float64', 'string'
            // myBLE.startNotifications(myCharacteristic, handleNotifications, 'string');
        }
    }
    updateStatus();
}

// A function that will be called once got characteristics
function handleNotifications(data) {
    myValue = data;
    if (myValue != undefined) {
        if (myValue.indexOf("|") > 0) {
            myValue = myValue.split("|");
            let temp = myValue[0];
            let humidity = myValue[1];
            setTempHumVals(temp + "°C " + humidity + "%");
        } else {
            myValue = myValue.split(":");
            if (myValue[0] >= 0) {
                setGaugeValue(myValue[0]);
                setLastRead();
                if (myValue[1] == 1) {
                    isSummer();
                } else {
                    isWinter();
                }
            } else {
                console.log("PING");
            }
        }
    } else {
        console.log("Data is undefined");
    }
}

// A function to stop notifications
function stopNotifications() {
    myBLE.stopNotifications(myCharacteristic);
}