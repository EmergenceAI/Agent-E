let awaitingUserResponse = false; // flag to check if the agent is awaiting user response

// disabled and enabled styles as injected style element
function injectOveralyStyles() {
  // Create a new style element
  let style = document.createElement('style');
  // Set the styles
  style.textContent = `
  @font-face {
    font-family: 'CircularXX';
    src: url('https://assets.website-files.com/627028e6193b2d840a066eab/627028e6193b2d9dd2066edf_CircularXXWeb-Book.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: auto;
}
@font-face {
    font-family: 'CircularXXLight';
    src: url('https://assets.website-files.com/627028e6193b2d840a066eab/627028e6193b2d710b066eda_CircularXXWeb-Light.woff2') format('woff2');
    font-weight: 300;
    font-style: normal;
    font-display: auto;
}
::-webkit-scrollbar {
    width: 6px;
    border: solid 3px transparent;
}

::-webkit-scrollbar-track {
    background-color: transparent;
}

::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.4);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
        background-color: rgba(255, 255, 255, 0.6);
    }

  .disabled {
      opacity: 0.95;
  }

  .pre-line {
    white-space: pre-line;
  }

  .enabled {
      opacity: 1;
  }

  #closebutton{
    width:25px;
    height:25px;
    min-width:25px;
    min-height:25px;
    position: absolute;
    top: 10px;
    right: 10px;
    color:darkgray;
    cursor: pointer;
    border: 1px solid lightgray;
    z-index: 20000001;
    background: white;

  }
  #closebutton:hover{
    border: 1px solid orange;
    color:black;
    font-weight: bold;
  }

  .collapsed{
  cursor: pointer;
  background-color: rgba(0, 0, 0, 0.1);
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  width: 5vh;
  height: 5vh;
  border-radius: 50%;
  right: 1.5vw;
  bottom: 1.5vw;
  padding: 0.5%;
  box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 20px
  }

  .chat-container {
    margin:1%,1%,1%,1%;
    width: 25vw;
    height:60vh;
    bottom: 2vh;
    position: relative;
    top: 6%;
    box-sizing: border-box; /* Include padding in the width and height calculations */
  } 
  
  .icon{
    width: 25px;
    border-radius: 50%;
    height: 25px;
  }


  
  .chat-input{
    display: flex;
    flex-direction: row;
    gap:2%;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-top:2vh;
  }

  #user-input {
    flex: 1;
    padding: 3px 3px;
    border: 1px solid #ccc;
    border-radius: 3px;
    width:80%;	
    resize: none;
    font-family: 'CircularXX';
    font-size: 14px;
    display: flex; 
    vertical-align: middle;
    text-align: middle;
    align-items: center;
    justify-content: center;
    border-color: #ccc;
    background: white;
    color:black;
    line-height: 1.2;
    min-height: calc(1.2em * 2);
    scrollbar-width: thin;
  }

  #user-input:focus {
    outline: none !important;
    border:1px solid orange;
    box-shadow: 0 0 10px #719ECE;
  }
  #send-btn {
    padding: 5px;
    margin-left: 5px;
    border: 1px solid #ccc;
    border-radius: 3px;
    cursor: pointer;
    color:black;
    opacity: 0.9;
    background: white;
    height:100%;
    font-family: 'CircularXX';
  }

  #send-btn:hover{
  background: orange;
  opacity: 1;

  }

  .highlight_overlay{
    box-shadow: 1px 1px 1px 1px rgb(50 50 50 / 40%);
    border-radius: 10px;
    border: 1px solid #ccc;
    bottom:3px;
    right:5px;
    padding: 1%;
    padding-top:30px;
    background: rgba(255, 255, 255, 1.0);
  }
  #chat-box {
    overflow-y: auto;
    scrollbar-width: thin;
    height: 90%;
    width:100%;
    display: flex;
    flex-direction: column;
    gap:1%;
    margin:1%;
    padding-bottom:1%;
    margin-top:10%;
  }
  
  #agentDriveAutoOverlay {
    position: fixed;
    min-width: 30px;
    min-height: 30px;
    margin-left: auto;
    margin-right: auto;
    z-index:20000000;
    scrollbar-color: gray lightgray; 
    margin-bottom: 1%;
  }

  .agent1{
    background: blueviolet;
    border-radius: 50%;
  }
  
  .agent2{
    background: rgba(150, 255, 150, 1);
    border-radius: 50%;
  }
  .user{
    background: orange;
    border-radius: 50%;
  }

  .input-container {
    display: flex;
    padding: 0%;
    height:8%;
  }
  
  .chat{
    width: 80%;
    color: black;
    overflow-wrap: break-word;
    font-family: 'CircularXX';
    font-size: 14px;
  }

  .agent1text{
    text-align: left;
    justify-content: flex-start;
    margin-right: auto;
    margin-left: auto;
    font-family: 'CircularXX';
    padding: 5%;
    min-height: 30px;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0.04) 0%, rgba(0, 0, 0, 0.12) 100%);
    box-shadow: 1px 1px 1px 1px rgb(150 150 150 / 60%);
    padding-left: 10px;
    border-radius: 20px;
    border: 1px solid blueviolet;
    width:72%;
  }
  .agent2text{
    text-align: left;
    justify-content: flex-start;
    margin-right: auto;
    margin-left: auto;
    font-family: 'CircularXX';
    padding: 5%;
    min-height: 30px;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0.04) 0%, rgba(0, 0, 0, 0.12) 100%);
    box-shadow: 1px 1px 1px 1px rgb(150 150 150 / 60%);
    padding-left: 10px;
    border-radius: 20px;
    border: 1px solid rgba(150, 255, 150, 1);
    width:72%;
  }

  .usertext{
    text-align: right;
    justify-content: flex-start;
    margin-right: auto;
    margin-left: auto;
    font-family: 'CircularXX';
    padding: 5%;
    min-height: 30px;
    width:72%;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0.04) 0%, rgba(0, 0, 0, 0.20) 100%)
    /* White Glass Effect */
    box-shadow: 8px 8px 16px rgba(0, 0, 0, 0.12), inset 1px 1px 2px rgba(255, 255, 255, 0.64), inset -1px -1px 2px rgba(255, 255, 255, 0.4);
    border-radius: 20px;
    color: black;
    border: 1px solid orange;
  }

  
  @keyframes automation_blink {
    0% { border-color: rgba(128, 0, 128, 1); }
    50% { border-color: rgba(128, 0, 128, 1); }
    100% { border-color: rgba(128, 0, 128, 0); }
  }
  
  .ui_automation_pulsate {
    border-width: 2px !important;
    border-style: solid !important;
    animation: automation_blink 5s linear 1 forwards !important;
  }
`;
  // Append the style element to the head of the document
  document.head.appendChild(style);
}
let savedSelection = null;

function showCollapsedOverlay() {
  removeOverlay();
  window.overlay_state_changed(true);
  let newDiv = document.createElement("div");
  newDiv.id = "agentDriveAutoOverlay";
  newDiv.classList.add("collapsed");
  newDiv.setAttribute("aria-hidden", "true");

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" height="800" width="800" viewBox="0 0 64 64" xml:space="preserve"><style>.st3{fill:#fff}.st4{fill:#4f5d73}</style><g id="Layer_1"><circle cx="32" cy="32" r="32" fill="#9c27b0"/><path d="M52 32c0-9.9-9-18-20-18s-20 8.1-20 18c0 9.6 8.3 17.4 18.8 17.9.7 3.7 1.2 6.1 1.2 6.1s5-3 9.6-8.2C47.8 44.7 52 38.8 52 32z" fill="#231f20" opacity=".2"/><path class="st3" d="M49 28.8C49 43.8 32 54 32 54s-9.4-42 0-42 17 7.5 17 16.8z" fill="#000000"/><ellipse class="st3" cx="32" cy="30" rx="20" ry="18" fill="#000000"/><circle class="st4" cx="32" cy="30" r="2" fill="#000000"/><circle class="st4" cx="40" cy="30" r="2" fill="#000000"/><circle class="st4" cx="24" cy="30" r="2" fill="#000000"/></g></svg>`;
  let encodedSvg = encodeURIComponent(svg);
  let svgUrl = 'data:image/svg+xml;utf8,' + encodedSvg;

  document.body.appendChild(newDiv);
  let element = document.getElementById('agentDriveAutoOverlay');
  element.style.backgroundImage = `url("${svgUrl}")`;
  document.getElementById('agentDriveAutoOverlay').addEventListener('mouseover', function () {
    this.style.transform = 'scale(1.1)';
  });

  document.getElementById('agentDriveAutoOverlay').addEventListener('mouseout', function () {
    this.style.transform = 'scale(1)';
  });
  document.getElementById('agentDriveAutoOverlay').addEventListener('click', function () {
    showExpandedOverlay();
  });
}

function removeOverlay() {
  let element = document.getElementById("agentDriveAutoOverlay");
  if (element) {
    element.parentNode.removeChild(element);
  }
}


function clearOverlayMessages() {
  try {
    let chatBox = document.getElementById('chat-box');
    if (!chatBox) {
      return;
    }
    console.log("Clearing chat box");
    while (chatBox.firstChild) {
      chatBox.removeChild(chatBox.firstChild);
    }
  } catch (error) {
    //No action can be taken at this point. Just ensure subsequent messages are not affected
    console.error("Error clearing chat box", error);
  }
}

function createIcon(className) {
  let icon = document.createElement("div");
  icon.className = `icon ${className}`;
  return icon;
}

function showExpandedOverlay() {
  removeOverlay();
  window.overlay_state_changed(false);
  console.log("showing  expanded overlay");
  let newDiv = document.createElement("div");
  newDiv.id = "agentDriveAutoOverlay";
  newDiv.classList.add("highlight_overlay");
  newDiv.classList.add("agentDriveAutoOverlay");
  newDiv.setAttribute("aria-hidden", "true");

  let closeButton = document.createElement("button");
  closeButton.id = "closebutton";
  closeButton.textContent = "X";
  closeButton.onclick = function () {
    showCollapsedOverlay();
  };

  // Append the close button to the newDiv
  newDiv.appendChild(closeButton);

  let chatContainer = document.createElement("div");
  chatContainer.className = "chat-container";

  let chatBox = document.createElement("div");
  chatBox.id = "chat-box";

  let chatInput = document.createElement("div");
  chatInput.className = "chat-input";

  let iconAgent1 = createIcon("agent1");

  chatBox.appendChild(chatInput);

  let inputContainer = document.createElement("div");
  inputContainer.className = "input-container";

  let userInput = document.createElement("textarea");
  userInput.id = "user-input";
  userInput.placeholder = "Type the task for the agent...";

  let sendBtn = document.createElement("button");
  sendBtn.id = "send-btn";
  sendBtn.textContent = "Send";

  inputContainer.appendChild(userInput);
  inputContainer.appendChild(sendBtn);

  chatContainer.appendChild(chatBox);
  chatContainer.appendChild(inputContainer);

  newDiv.appendChild(chatContainer);

  document.body.appendChild(newDiv);

  document.getElementById('send-btn').addEventListener('click', function () {
    let task = document.getElementById('user-input').value
    if (task && !isDisabled()) {
      if (awaitingUserResponse) {
        addUserMessage(task);
        document.getElementById('user-input').value = "";
      } else {
        console.log(`Sending ${task} to server`);
 
        addUserMessage(task);
        window.process_task(task)
        document.getElementById('user-input').value = "";
      }
    }
    else {
      console.log("Empty message no task to send");
    }
  });

  userInput.addEventListener('focus', function() {
    if (window.getSelection().rangeCount > 0) {
        let selectedText = window.getSelection().toString();
        console.log(selectedText);
        if (selectedText) {
          document.getElementById('user-input').value = selectedText +  '\n';
          setTimeout(function() {
            userInput.selectionStart = userInput.selectionEnd = userInput.value.length;
            userInput.scrollTop = userInput.scrollHeight;
        }, 0);
         
         }
    }
});

userInput.addEventListener('blur', function() {
    if (savedSelection) {
        let selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(savedSelection);
    }
});

  document.getElementById('user-input').addEventListener('keydown', function (event) {
    // Check if the pressed key is the Enter key
    if (event.key === "Enter") {
      event.preventDefault();

      let targetElement = document.getElementById('send-btn');

      // Create a new click event
      let clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true
      });

      // Dispatch the click event on the send button
      targetElement.dispatchEvent(clickEvent);
    }
  });
  focusOnOverlayInput();
}


function focusOnOverlayInput() {
  document.getElementById('user-input').focus();
}

function addMessage(message, sender) {
  //console.log(`Adding ${sender} message: ${message}`);
  let newDiv = document.createElement("div");
  newDiv.classList.add("chat-input");

  let iconDiv1 = document.createElement("div");
  iconDiv1.classList.add("icon");

  let chatDiv = document.createElement("div");
  chatDiv.classList.add("chat");

  let iconDiv2 = document.createElement("div");
  iconDiv2.classList.add("icon");

  newDiv.appendChild(iconDiv1);
  newDiv.appendChild(chatDiv);
  newDiv.appendChild(iconDiv2);
  let parsedMessage = message;

  try {
    parsedMessage = JSON.parse(message);
  } catch (e) {
    //console.log("Message is not in JSON format, using original message.");
  }

  // Customize based on the sender
  if (sender === "system") {
    iconDiv1.classList.add("agent1");
    chatDiv.classList.add("agent1text", "pre-line");
    chatDiv.innerText = parsedMessage;
  } else if (sender === "user") {
    iconDiv2.classList.add("user");
    chatDiv.classList.add("usertext", "pre-line");
    chatDiv.innerText = parsedMessage;
  }

  let chatBox = document.getElementById('chat-box');
  chatBox.appendChild(newDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
  newDiv.scrollIntoView({ behavior: 'instant' });

  if (sender === "user" && awaitingUserResponse) {
    awaitingUserResponse = false;
    // Notify the server that the user has responded to the agent's prompt
    window.user_response(message);
  }
}


function addSystemMessage(message, is_awaiting_user_response = false) {
  awaitingUserResponse = is_awaiting_user_response;
  addMessage(message, "system");
}

function addUserMessage(message) {
  addMessage(message, "user");
}


function disableOverlay() {
  let element = document.getElementById("agentDriveAutoOverlay");
  element.classList.remove("enabled");
  element.classList.add("disabled");
}

function isDisabled() {
  let element = document.getElementById("agentDriveAutoOverlay");
  return element.classList.contains("disabled");
}

function enableOverlay() {
  let element = document.getElementById("agentDriveAutoOverlay");
  element.classList.add("enabled");
  element.classList.remove("disabled");
  document.getElementById('user-input').focus();
}

function commandExecutionCompleted() {
  console.log("Command execution completed");
}

injectOveralyStyles();
