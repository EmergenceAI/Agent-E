let awaitingUserResponse = false; // flag to check if the agent is awaiting user response
let speechInputOngoing = false;
var messageTosend = "";
let speechRecognition;
// disabled and enabled styles as injected style element
function injectOveralyStyles() {
  // Create a new style element
  let style = document.createElement('style');
  // Set the styles
  style.textContent = `
@import url(https://fonts.googleapis.com/earlyaccess/notosanssc.css);

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
      opacity: 0.85;
      pointer-events: none;
  }

  .pre-line {
    white-space: pre-line;
  }

  .enabled {
      opacity: 1;
      pointer-events: auto;
  }

  #closebutton{
    width:30px;
    height:30px;
    min-width:30px;
    min-height:30px;
    margin-left: auto;
    color:darkgray;
    cursor: pointer;
    background: transparent;
    transition: transform 0.2s ease; 
    border: None;
  }
  #closebutton:hover{
    transform: scale(1.1);
  }

  #closebutton:active{
    transform: scale(0.8);
  }

  @keyframes gradient-animation {
  0% {background-position: 100% 0%}
  100% {background-position: 15% 100%}
  }

  @keyframes rotate {
    100% {
      transform: rotate(1turn);
    }
  }
  .processing{
  background: linear-gradient(90deg, 
                              rgba(255, 0, 255, 1) 0%,  /* Bright Magenta */
                              rgba(0, 191, 255, 1) 100%    /* Deep Sky Blue */
                              );
  background-size: 100% 200%;
  animation: rotate 1s linear infinite;
  }
  
  .init{
    background: lightgray;
  }
  
  .done{
  background: lightgreen;
  }

  .processingLine {
    background: linear-gradient(45deg, 
                                rgba(255, 0, 0, 1) 0%,    /* Red */
                                rgba(255, 127, 0, 1) 25%,  /* Orange */
                                rgba(0, 255, 0, 1) 50%,    /* Green */
                                rgba(0, 0, 255, 1) 75%,    /* Blue */
                                rgba(255, 0, 0, 1) 90%,    /* Red */
                                rgba(255, 0, 0, 1) 100%    /* Red */
                                );
    background-size: 500% 100%;
    animation: gradient-animation 3s linear infinite;
  }

  .initStateLine{
  background: lightgray;
  }

  .doneStateLine{
  background: lightgreen;
  }


  .collapsed{
  cursor: pointer;
  background-color: rgba(0, 0, 0, 0.1);
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  width: 6vh;
  height: 6vh;
  border-radius: 50%;
  right: 1.5vw;
  bottom: 1.5vw;

  box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 20px
  }

  .chat-container {
    margin:1%,1%,1%,1%;
    width: 30vw;
    min-width: 350px;
    height:70vh;
    bottom: 2vh;
    position: relative;
    display: flex;
    flex-direction: column;
    top: 6%;
    padding: 1%;
    box-sizing: border-box; 
  } 
  
  .icon{
    width: 25px;
    border-radius: 50%;
    height: 25px;
  }

.loader {
    width: 24px;
    height: 25px;
    border: 5px solid #DDD;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
    }

    @keyframes rotation {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
    } 
  
  .chat-input{
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 95%;
    margin-top:1.5vh;
  }

  .agent{
    justify-content: flex-start;
  }
  
  .user{
    justify-content: flex-end;
  }

  #user-input {
    flex: 1;
    padding: 3px 3px;
    border: transparent;
    width:100%;	
    resize: none;
    font-family: 'Noto Sans SC';
    font-size: 1.6vh;
    min-font-size: 12px;
    line-height: 1.5;
    display: flex; 
    vertical-align: middle;
    text-align: middle;
    align-items: center;
    justify-content: center;
    border-color: #ccc;
    background: white;
    color:black;
    min-height: calc(1.2em * 2);
    scrollbar-width: thin;
  }

  #user-input:focus {
    outline: none !important;
    border:1px solid transparent;
  }
  #send-btn {
    cursor: pointer;
    transition: transform 0.2s ease; 
  }

  #send-btn:hover{
  transform: scale(1.1);
  }

  .highlight_overlay{
    box-shadow: 1px 1px 1px 1px rgb(50 50 50 / 40%);
    border-radius: 16px;
    border: 1px solid #E1DEE2;
    bottom:3px;
    right:5px;
    background: #FBFAFA;
  }
  #chat-box {
    overflow-y: auto;
    scrollbar-width: thin;
    height: 90%;
    display: flex;
    flex-direction: column;
    gap:1%;
    margin:1% 5%;
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
    display: flex;
    flex-direction: column;
  }

  .agent1{
    background: blueviolet;
    border-radius: 50%;
  }
  
  .agent2{
    background: rgba(150, 255, 150, 1);
    border-radius: 50%;
  }


  .input-container {
    display: flex;
    flex-direction: column;
    margin: 1% 3%;
    padding: 1%;
    height:20%;
    background: white;
    border: 1px solid #E1DEE2;
    border-radius: 8px;
  }
  
  .chat{
    width: 80%;
    color: black;
    overflow-wrap: break-word;
    font-family: 'Noto Sans SC';

  }

  .agent1text{
    text-align: left;
    justify-content: flex-start;
    font-family: 'Noto Sans SC';
    padding: 2% 4%;
    font-size: 1.5vh;
    min-font-size: 12px;
    min-height: 30px;
    background: #EEEEEF;
    line-height: 1.7;
    border-radius: 10px;
    width:auto;
    max-width: 90%;

  }

  .usertext{
    text-align: right;
    justify-content: flex-end;
    align-items: flex-end;
    font-family: 'Noto Sans SC';
    font-size: 1.5vh;
    min-font-size: 12px;
    padding: 2% 4%;
    line-height: 1.7;
    min-height: 30px;
    width:auto;
    background: #ECEBF3;
    border-radius: 10px;
    color: black;
  }
  
  .agentstep{
  color: #4B4B4B;
  }
  .agentplan{
  color: #4B4B4B;
  }
  .agentanswer{
  color: black;
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

  .toggle {
  all: unset;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  width: 44px;
  height: 24px;
  margin: 0;
  display: inline-block;
  position: relative;
  border-radius: 50px;
  overflow: hidden;
  outline: none;
  border: none;
  cursor: pointer;
  background-color: #E1DEE2;
  transition: background-color ease 0.3s;
  align-self: center;
}
.toggle:focus {
  border: none; !important;
  outline: none; !important;
}
.toggle:before {
  content: "";
  display: block;
  position: absolute;
  z-index: 2;
  width: 20px;
  height: 20px;
  background: #fff;
  left: 2px;
  top: 2px;
  border-radius: 50%;
  color: #fff;
  text-shadow: -1px -1px rgba(0,0,0,0.15);
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
  transition: all cubic-bezier(0.3, 1.5, 0.7, 1) 0.3s;
}

.toggle:checked {
  background-color: #786E96;
}

.toggle:checked:before {
  left: 20px;
}
`;
  // Append the style element to the head of the document
  document.head.appendChild(style);
}
let savedSelection = null;
let show_details = true;

if (!('webkitSpeechRecognition' in window)) {
  console.log("Speech API not supported");
}
else {
  speechRecognition = new webkitSpeechRecognition();  
  speechRecognition.continuous = true;
  speechRecognition.interimResults = true;
  speechRecognition.lang = "en-US";

  speechRecognition.onstart = function () {
      speechInputOngoing=true;
  }
  speechRecognition.onend = function () {
      speechInputOngoing = false;
  }    
}

function showCollapsedOverlay(processing_state = "processing", steps) {
  show_details = steps;
  removeOverlay();
  window.overlay_state_changed(true);
  let collapsed_agente = document.createElement("div");
  collapsed_agente.id = "agentDriveAutoOverlay";
  collapsed_agente.classList.add("collapsed");
  collapsed_agente.style.backgroundColor = "transparent";
  collapsed_agente.setAttribute("aria-hidden", "true");
  collapsed_agente.style.justifyContent = "center";
  let wrapper = document.createElement("div");
  wrapper.style.position = "relative";
  wrapper.style.width = "6vh";
  wrapper.style.height = "6vh";
  wrapper.style.justifyContent = "center";
  let logodiv= document.createElement("div");
  logodiv.style.width = "5.4vh";
  logodiv.style.height = "5.4vh";
  logodiv.style.left = "0.3vh";
  logodiv.style.top = "0.3vh";
  let borderdiv = document.createElement("div");
  borderdiv.style.width = "6vh";
  borderdiv.style.height = "6vh";
  borderdiv.style.borderRadius = "50%";

  let logo = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6.5" y="7.5" width="11" height="11" rx="0.5" stroke="#827C8C"/><rect x="-0.5" y="0.5" width="3" height="5" rx="0.5" transform="matrix(-1 0 0 1 6 10)" stroke="#827C8C"/><rect x="-0.5" y="0.5" width="3" height="5" rx="0.5" transform="matrix(-1 0 0 1 20 10)" stroke="#827C8C"/><path d="M12 4V7.5" stroke="#827C8C" stroke-linecap="round"/><rect x="8.5" y="11.5" width="7" height="3" rx="1.5" stroke="#827C8C"/></svg>`;
  let encodedSvg = encodeURIComponent(logo);
  let svgUrl = 'data:image/svg+xml;utf8,' + encodedSvg;
  logodiv.style.backgroundImage = `url("${svgUrl}")`;
  logodiv.style.backgroundRepeat = "no-repeat";
  logodiv.style.backgroundSize = "contain";
  logodiv.style.borderRadius = "50%";
  logodiv.style.backgroundPosition = "center";
  logodiv.style.backgroundColor = "white";
  logodiv.style.alignSelf = "center";
  borderdiv.style.position = "absolute";
  borderdiv.style.top = "0";
  borderdiv.style.left = "0";
  borderdiv.id="AgentEOverlayBorder";
  logodiv.style.position = "absolute";
  logodiv.style.justifySelf = "center";
  wrapper.appendChild(borderdiv);
  wrapper.appendChild(logodiv);
  collapsed_agente.appendChild(wrapper);
  document.body.appendChild(collapsed_agente);
  
  updateOverlayState(processing_state, true);
  
  let element = document.getElementById('agentDriveAutoOverlay');
  document.getElementById('agentDriveAutoOverlay').addEventListener('mouseover', function () {
    this.style.transform = 'scale(1.1)';
  });

  document.getElementById('agentDriveAutoOverlay').addEventListener('mouseout', function () {
    this.style.transform = 'scale(1)';
  });
  document.getElementById('agentDriveAutoOverlay').addEventListener('click', function () {
    let ui_state = document.getElementById("AgentEOverlayBorder").classList.contains("init") ? "init" : document.getElementById("AgentEOverlayBorder").classList.contains("processing") ? "processing" : "done";
    showExpandedOverlay(ui_state, show_details);
  });
}

function removeOverlay() {
  let element = document.getElementById("agentDriveAutoOverlay");
  if (element) {
    element.parentNode.removeChild(element);
  }
}

function clearOverlayMessages(keep_default=false) {
  try {
    let chatBox = document.getElementById('chat-box');
    if (!chatBox) {
      return;
    }
    while (chatBox.firstChild) {
      chatBox.removeChild(chatBox.firstChild);
    }
  } catch (error) {
    //No action can be taken at this point. Just ensure subsequent messages are not affected
    console.error("Error clearing chat box", error);
  }
}

function updateOverlayState(processing_state, is_collapsed) 
{
  if (is_collapsed) {
    let borderdiv = document.getElementById("AgentEOverlayBorder");
    if (processing_state=="init"){
      borderdiv.classList.add("init");
      borderdiv.classList.remove("processing");
      borderdiv.classList.remove("done");
    }
    else if (processing_state=="processing"){
      borderdiv.classList.remove("init");
      borderdiv.classList.add("processing");
      borderdiv.classList.remove("done");
    }
    else if (processing_state=="done"){
      borderdiv.classList.remove("init");
      borderdiv.classList.remove("processing");
      borderdiv.classList.add("done");
    }
  } else {
    let animation = document.getElementById("AgentEExpandedAnimation");
    if (processing_state=="init"){
      animation.classList.remove("processingLine");
      animation.classList.add("initStateLine");
      animation.classList.remove("doneStateLine");
      enableOverlay();
    }
    else if (processing_state=="processing"){
      animation.classList.add("processingLine");
      animation.classList.remove("initStateLine");
      animation.classList.remove("doneStateLine");
      disableOverlay();
    }
    else if (processing_state=="done"){
      animation.classList.remove("processingLine");
      animation.classList.remove("initStateLine");
      animation.classList.add("doneStateLine");
      enableOverlay();
    }
  }
}

function showExpandedOverlay(processing_state = "init", show_steps=true) {
  ui_state = processing_state;
  show_details = show_steps;
  let agente_logo = `<svg width="85" height="12" viewBox="0 0 85 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0 11.8027L3.43562 0.213699H8.35069L11.8027 11.8027H9.3863L8.23562 7.85753H3.53425L2.38356 11.8027H0ZM4.10959 5.86849H7.66027L6.18082 0.80548H5.58904L4.10959 5.86849Z" fill="#6B6673"/><path d="M19.0946 12C15.6096 12 13.7028 9.56712 13.7028 6.09863C13.7028 2.4 15.9055 0 19.4562 0C22.4151 0 24.5685 1.70959 24.9631 4.35616H22.6124C22.3822 2.87671 21.2151 1.9726 19.5713 1.9726C17.3192 1.9726 16.0535 3.58356 16.0535 6.09863C16.0535 8.35068 17.0726 10.011 19.637 10.011C21.7576 10.011 22.974 8.94247 22.974 7.15068H19.374V5.40822H23.9768C24.8151 5.40822 25.2918 5.85205 25.2918 6.69041V11.8027H23.0069V10.7671L23.4672 8.92603H22.8589C22.8754 9.6 22.4973 12 19.0946 12Z" fill="#6B6673"/><path d="M28.7192 11.8027V0.213699H37.3987V2.20274H31.0206V5.04658H36.5768V6.95342H31.0206V9.8137H37.3987V11.8027H28.7192Z" fill="#6B6673"/><path d="M40.533 11.8027V0.213699H45.0536L49.1631 11.211H49.7385L49.3275 9.76438V0.213699H51.6125V11.8027H47.0919L42.9823 0.80548H42.3905L42.8179 2.25205V11.8027H40.533Z" fill="#6B6673"/><path d="M54.4378 0.213699H64.4159V2.20274H60.5693V11.8027H58.2844V2.20274H54.4378V0.213699Z" fill="#6B6673"/><path d="M63.9401 6.6411H72.4551V8.30137H63.9401V6.6411Z" fill="#6B6673"/><path d="M75.3643 11.8027V0.213699H84.0438V2.20274H77.6657V5.04658H83.2219V6.95342H77.6657V9.8137H84.0438V11.8027H75.3643Z" fill="#6B6673"/></svg>`;
  let close_icon = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 10L10 10L10 5" stroke="#827C8C"/><path d="M19 14L14 14L14 19" stroke="#827C8C"/><path d="M14 5L14 10L19 10" stroke="#827C8C"/><path d="M10 19L10 14L5 14" stroke="#827C8C"/><path d="M6.35355 5.64645C6.15829 5.45118 5.84171 5.45118 5.64645 5.64645C5.45118 5.84171 5.45118 6.15829 5.64645 6.35355L6.35355 5.64645ZM10.3536 9.64645L6.35355 5.64645L5.64645 6.35355L9.64645 10.3536L10.3536 9.64645Z" fill="#827C8C"/><path d="M17.6464 18.3536C17.8417 18.5488 18.1583 18.5488 18.3536 18.3536C18.5488 18.1583 18.5488 17.8417 18.3536 17.6464L17.6464 18.3536ZM13.6464 14.3536L17.6464 18.3536L18.3536 17.6464L14.3536 13.6464L13.6464 14.3536Z" fill="#827C8C"/><path d="M18.3536 6.35355C18.5488 6.15829 18.5488 5.84171 18.3536 5.64645C18.1583 5.45119 17.8417 5.45119 17.6464 5.64645L18.3536 6.35355ZM14.3536 10.3536L18.3536 6.35355L17.6464 5.64645L13.6464 9.64645L14.3536 10.3536Z" fill="#827C8C"/><path d="M5.64645 17.6464C5.45118 17.8417 5.45118 18.1583 5.64645 18.3536C5.84171 18.5488 6.15829 18.5488 6.35355 18.3536L5.64645 17.6464ZM9.64645 13.6464L5.64645 17.6464L6.35355 18.3536L10.3536 14.3536L9.64645 13.6464Z" fill="#827C8C"/></svg>`;
  let icon = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6.5" y="7.5" width="11" height="11" rx="0.5" stroke="#827C8C"/><rect x="-0.5" y="0.5" width="3" height="5" rx="0.5" transform="matrix(-1 0 0 1 6 10)" stroke="#827C8C"/><rect x="-0.5" y="0.5" width="3" height="5" rx="0.5" transform="matrix(-1 0 0 1 20 10)" stroke="#827C8C"/><path d="M12 4V7.5" stroke="#827C8C" stroke-linecap="round"/><rect x="8.5" y="11.5" width="7" height="3" rx="1.5" stroke="#827C8C"/></svg>`;
  removeOverlay();
  window.overlay_state_changed(false);
  let newDiv = document.createElement("div");
  newDiv.id = "agentDriveAutoOverlay";
  newDiv.classList.add("highlight_overlay");
  newDiv.classList.add("agentDriveAutoOverlay");
  newDiv.setAttribute("aria-hidden", "true");
  newDiv.setAttribute("tabindex", "0");

  newDiv.addEventListener('keydown', function(event) {
    let final_transcript = "";
    let userInput = document.getElementById('user-input');
    if (event.key.toLowerCase() === 'm' && document.activeElement !== userInput && isDisabled() == false) {
        if (speechInputOngoing == false) {
                console.log("M Key down, activating speech recognition");
                if (!speechRecognition.listening) {
                    speechRecognition.start();
                }
                try {
                    inChime.play()
                } catch (error) {
                }
                messageTosend = "";
                speechRecognition.onresult = function (event) {
                    let interim_transcript = '';
                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            final_transcript += event.results[i][0].transcript;
                            const elem = document.getElementById("user-input");
                            elem.innerHTML = final_transcript;
                            messageTosend = final_transcript;

                        } else {
                            interim_transcript += event.results[i][0].transcript;
                            const elem = document.getElementById("user-input");
                            elem.innerHTML = final_transcript+ " "+ interim_transcript;
                            console.log("Interim : " + interim_transcript);
                        }
                    }
                };
            }
    }
});

newDiv.addEventListener('keyup', function(event) {
   
    if (event.key.toLowerCase() === 'm' && document.activeElement !== userInput) {
      if (speechInputOngoing) {
        try {
            outChime.play()
        } catch (error) {

        }
        speechRecognition.stop();
        console.log("Stopped speech recognition");
        setTimeout(function () {
          console.log("Inside settimeout");
          let userInput = document.getElementById('user-input');
          let messageTosend = userInput.innerHTML;
          userInput.innerHTML = "";
          userInput.blur();
          userInput.dispatchEvent(new FocusEvent('blur'));
          console.log("Sending to server from M key up " + messageTosend);
            if (messageTosend.trim()!="") {
                addUserMessage(messageTosend);
                disableOverlay();
                window.process_task(messageTosend)
                console.log("Sending to server from M key up " + messageTosend);
                messageTosend = "";
            }

        }, 100);
    }
    }
});
  let header = document.createElement("div");
  header.style.display = "flex";
  header.style.flexDirection = "row";
  header.style.margin = "4%";
  
  let logoIcon= document.createElement("div");
  logoIcon.style.width = "25px";
  logoIcon.style.height = "25px";
  logoIcon.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(icon)}')`;
  logoIcon.style.backgroundRepeat = "no-repeat";
  logoIcon.style.backgroundSize = "contain";
  logoIcon.style.backgroundPosition = "bottom";
  logoIcon.style.order = 1;
  logoIcon.style.alignSelf = "flex-end";
  logoIcon.style.marginRight = "1%";

  let logoDiv = document.createElement("div");
  logoDiv.style.width = "100px";
  logoDiv.style.height = "25px";
  logoDiv.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(agente_logo)}')`;
  logoDiv.style.backgroundRepeat = "no-repeat";
  logoDiv.style.backgroundSize = "contain";
  logoDiv.style.backgroundPosition = "bottom";
  // Style the logoDiv and button
  logoDiv.style.order = 1;


  let closeButton = document.createElement("button");
  closeButton.id = "closebutton";
  closeButton.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(close_icon)}')`;
  closeButton.style.backgroundRepeat = "no-repeat";
  closeButton.style.backgroundSize = "contain";
  closeButton.style.backgroundPosition = "bottom";
  closeButton.onclick = function () {
    let ui_state = document.getElementById("AgentEExpandedAnimation").classList.contains("initStateLine") ? "init" : document.getElementById("AgentEExpandedAnimation").classList.contains("processingLine") ? "processing" : "done";
    showCollapsedOverlay(ui_state, show_details);
  };
  closeButton.style.order = 3;
  header.appendChild(logoIcon);
  header.appendChild(logoDiv);
  let animation = document.createElement("div");
  animation.id = "AgentEExpandedAnimation";
  animation.style.height = "2px";
  animation.style.width = "100%";
 
  header.appendChild(closeButton);
  // Append the close button to the newDiv
  newDiv.appendChild(header);


  newDiv.appendChild(animation);
  let chatContainer = document.createElement("div");
  chatContainer.className = "chat-container";

  let chatBox = document.createElement("div");
  chatBox.id = "chat-box";

  let chatInput = document.createElement("div");
  chatInput.className = "chat-input";
  chatBox.appendChild(chatInput);

  let inputContainer = document.createElement("div");
  inputContainer.className = "input-container";
  inputContainer.id = "input-container";
  let userInput = document.createElement("textarea");
  userInput.id = "user-input";
  userInput.placeholder = "What can i help you solve today?";
  userInput.addEventListener('input', function(event) {
    let text = event.target.value;
    if (text.trim() == "") {
      let button_disabled_svg =`<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="40" height="40" rx="4" fill="#EEEEEF"/><path d="M15 20H25" stroke="#AEA9B4" stroke-width="1.5"/><path d="M20 15L25 20L20 25" stroke="#AEA9B4" stroke-width="1.5"/></svg>`;  
      let sendBtn = document.getElementById('send-btn');
      sendBtn.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(button_disabled_svg)}')`;
    }
    else{
      let button_enabled_svg= `<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="40" height="40" rx="4" fill="#252539"/><path d="M15 20H25" stroke="white" stroke-width="1.5"/><path d="M20 15L25 20L20 25" stroke="white" stroke-width="1.5"/></svg>`;
      let sendBtn = document.getElementById('send-btn');
      sendBtn.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(button_enabled_svg)}')`;
    }
    console.log('Text changed:', event.target.value);
  });
  let userinput_footer = document.createElement("div");
  userinput_footer.style.display = "flex";
  userinput_footer.style.flexDirection = "row";
  userinput_footer.style.justifyContent = "space-between";
  userinput_footer.style.alignItems = "center";
  userinput_footer.style.height = "40%";
  userinput_footer.style.margin = "2% 1%";
  userinput_footer.id="userinput_section"

  let toggleLabel = document.createElement("label");  // Create a new label element
  toggleLabel.textContent = "Show Details";  // Set the text content of the label
  toggleLabel.style.color = "#6B6673";  // Set the color of the label
  toggleLabel.style.fontFamily = "Noto Sans SC";  // Set the font of the label
  toggleLabel.style.fontSize = "14px";  // Set the font size of the label
  toggleLabel.style.fontWeight = "400";  // Set the font weight of the label
  toggleLabel.style.margin = "0px";  // Add some margin to the right of the label
  toggleLabel.style.marginRight = "10px";  // Add some margin to the right of the label
  
  let toggleSwitch = document.createElement("input");
  toggleSwitch.type = "checkbox";
  toggleSwitch.className = "toggle";
  toggleSwitch.style.margin = "0px";
  if (show_details){
    toggleSwitch.checked = true;
  }
  else{
    toggleSwitch.checked = false;
  }
  
  toggleSwitch.addEventListener('change', function() {
    if(this.checked) {
        show_details = true;
        window.show_steps_state_changed(true)
    } else {
      show_details = false;
      window.show_steps_state_changed(false)
    }
});

  let sendicon =`<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="40" height="40" rx="4" fill="#EEEEEF"/><path d="M15 20H25" stroke="#AEA9B4" stroke-width="1.5"/><path d="M20 15L25 20L20 25" stroke="#AEA9B4" stroke-width="1.5"/></svg>`;  
  let sendBtn = document.createElement("div");
  sendBtn.id = "send-btn";
  sendBtn.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(sendicon)}')`;
  sendBtn.style.backgroundRepeat = "no-repeat";
  sendBtn.style.backgroundSize = "contain";
  sendBtn.style.backgroundPosition = "right";
  sendBtn.style.width = "8%";
  sendBtn.style.height = "100%";
  sendBtn.style.marginLeft = "auto";
  
  userinput_footer.appendChild(toggleLabel);  // Add the label to the div
  userinput_footer.appendChild(toggleSwitch);
  userinput_footer.appendChild(sendBtn);

  inputContainer.appendChild(userInput);
  inputContainer.appendChild(userinput_footer);

  chatContainer.appendChild(chatBox);
  chatContainer.appendChild(inputContainer);

  newDiv.appendChild(chatContainer);

  let disclaimer = document.createElement("p");
  disclaimer.style.fontFamily = "Noto Sans SC";
  disclaimer.style.fontSize = "12px";
  disclaimer.style.color = "#6B6673";
  disclaimer.style.alignSelf = "center";
  disclaimer.style.position = "absolute";
  disclaimer.style.bottom = "0%";
  disclaimer.style.margin = "0% 0% 1% 0%";
  disclaimer.textContent = "Agent-E may make mistakes. Verify key info.";

  newDiv.appendChild(disclaimer);

  document.body.appendChild(newDiv);
  updateOverlayState(processing_state, false);
  document.getElementById('send-btn').addEventListener('click', function () {
    let task = document.getElementById('user-input').value
    let task_trimmed = task.trim();
    if (task_trimmed && !isDisabled() && task_trimmed.length > 0) {
      if (awaitingUserResponse) {
        addUserMessage(task);
        document.getElementById('user-input').value = "";
      } else {
        clearOverlayMessages();
        addUserMessage(task);
        disableOverlay();
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

function addMessage(message, sender, message_type = "plan") {
  let newDiv = document.createElement("div");
  newDiv.classList.add("chat-input");
  let chatDiv = document.createElement("div");
  chatDiv.classList.add("chat");

  let parsedMessage = message;

  try {
    parsedMessage = JSON.parse(message);
  } catch (e) {
    //console.log("Message is not in JSON format, using original message.");
  }

  // Customize based on the sender
  if (sender === "system") {
    newDiv.classList.add("agent");
    chatDiv.classList.add("agent1text", "pre-line");
      if (message_type === "step") {
      chatDiv.classList.add("agentstep");
      }
      else if (message_type === "plan" || message_type === "question") {
        chatDiv.classList.add("agentplan");
      }

      else if (message_type === "answer") {
      chatDiv.classList.add("agentanswer");
      }
      if ((message_type === "info" && message.includes("Task Completed")) || message_type==="question") {
      enableOverlay();
      }
    chatDiv.textContent = parsedMessage;
  } else if (sender === "user") {
    newDiv.classList.add("user")
    chatDiv.classList.add("usertext", "pre-line");
    chatDiv.textContent = parsedMessage;
  }
  newDiv.appendChild(chatDiv);
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

function addSystemMessage(message, is_awaiting_user_response = false, message_type = "plan") {
  // Function to actually add the message
  function executeAddMessage() {
    awaitingUserResponse = is_awaiting_user_response;
    addMessage(message, "system", message_type);
  }
    requestAnimationFrame(executeAddMessage);
}

function addUserMessage(message) {
  addMessage(message, "user");
}

function disableOverlay() {
  let input_field= document.getElementById("user-input");
  if(input_field){
    input_field.placeholder = "Processing...";
  }
}

function isDisabled() {
  let input_field= document.getElementById("user-input");
  if(input_field){
    if (input_field.placeholder === "Processing...") {
      return true;
    } 
  else {
    return false;
  }
  }
}


function enableOverlay() {
    let input_field= document.getElementById("user-input");
    if(input_field){
      input_field.placeholder = "What can i help you solve today?";
    }
}

function commandExecutionCompleted() {
  console.log("Command execution completed");
}

injectOveralyStyles();
