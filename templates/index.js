// Controller Animation Code
let controllerIndex = null;

window.addEventListener("gamepadconnected", (event) => {
  const gamepad = event.gamepad;
  controllerIndex = gamepad.index;
  console.log("connected");
});

window.addEventListener("gamepaddisconnected", (event) => {
  controllerIndex = null;
  console.log("disconnected");
});

function handleButtons(buttons) {
  for (let i = 0; i < buttons.length; i++) {
    const button = buttons[i];
    const buttonElement = document.getElementById(`controller-b${i}`);
    const selectedButtonClass = "selected-button";

    if (buttonElement) {
      if (button.value > 0) {
        buttonElement.classList.add(selectedButtonClass);
        buttonElement.style.filter = `contrast(${button.value * 150}%)`;
      } else {
        buttonElement.classList.remove(selectedButtonClass);
        buttonElement.style.filter = `contrast(100%)`;
      }
    }
  }
}

function updateStick(elementId, leftRightAxis, upDownAxis) {
  const multiplier = 25;
  const stickLeftRight = leftRightAxis * multiplier;
  const stickUpDown = upDownAxis * multiplier;

  const stick = document.getElementById(elementId);
  const x = Number(stick.dataset.originalXPosition);
  const y = Number(stick.dataset.originalYPosition);

  stick.setAttribute("cx", x + stickLeftRight);
  stick.setAttribute("cy", y + stickUpDown);
}

function handleSticks(axes) {
  updateStick("controller-b10", axes[0], axes[1]);
  updateStick("controller-b11", axes[2], axes[3]);
}

function gameLoop() {
  if (controllerIndex !== null) {
    const gamepad = navigator.getGamepads()[controllerIndex];
    handleButtons(gamepad.buttons);
    handleSticks(gamepad.axes);
  }
  requestAnimationFrame(gameLoop);
}

//Controller Servo Control Code
let joystickThreshold = 0.2;  // Threshold for joystick movement to avoid noise
let gamepadIndex;

window.addEventListener("gamepadconnected", (event) => {
    gamepadIndex = event.gamepad.index;
    console.log("Gamepad connected at index " + gamepadIndex);
});

window.addEventListener("gamepaddisconnected", (event) => {
    gamepadIndex = null;
    console.log("Gamepad disconnected from index " + event.gamepad.index);
});

function sendMotorCommand(direction) {
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `direction=${direction}`
    });
}

function handleJoystickInput() {
    const gamepad = navigator.getGamepads()[gamepadIndex];

    if (gamepad) {
        const leftStickX = gamepad.axes[0];  // Left joystick horizontal axis
        const leftStickY = gamepad.axes[1];  // Left joystick vertical axis

        if (leftStickY < -joystickThreshold) {
            sendMotorCommand('forward');  // Move forward if Y-axis is pushed up
        } else if (leftStickY > joystickThreshold) {
            sendMotorCommand('backward');  // Move backward if Y-axis is pushed down
        } else if (leftStickX < -joystickThreshold) {
            sendMotorCommand('left');  // Turn left if X-axis is pushed left
        } else if (leftStickX > joystickThreshold) {
            sendMotorCommand('right');  // Turn right if X-axis is pushed right
        } else {
            sendMotorCommand('stop');  // Stop if joystick is centered
        }
    }

    requestAnimationFrame(handleJoystickInput);  // Continuously check for input
}

requestAnimationFrame(handleJoystickInput);  // Start the input handling loop
gameLoop();
