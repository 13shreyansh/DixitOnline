import Button from "src/components/button.jsx"
import "src/App.css"
import "./prompt.css"
import socket from "../socketConfig.jsx";
import {useState} from "react";
import {backend_url} from "../backendUrl.jsx";

function Prompt(props) {

  const [inputText, setInputText] = useState("");

  var inputStyles = {
    "width": "100%",
    "height": "30px",
    "fontSize": "30px"
  };

  function handlePromptSubmit(event) {
    if(inputText.length > 0){
      socket.emit("enter_prompt", {
        "prompt": inputText
      })
      console.log("prompt submitted");
    }
  }

  function handleChange(e){
    setInputText(e.target.value);
  }

  var promptInfo;
  promptInfo = props.info.promptInfo || "Write a prompt that recreates the target image on the TV.";
  const challenge = props.info.challenge;

  return (
    <div id="prompt_container">
      <div id="prompt_info" className="info_text">
        {promptInfo}
      </div>
      {challenge && (
        <div id="challenge_card">
          <div id="challenge_title">{challenge.title}</div>
          <div id="challenge_description">{challenge.description}</div>
        </div>
      )}
      {props.info.target_image && (
        <img className="prompt_target_image" src={backend_url + props.info.target_image} alt="Target" />
      )}
      <input style={inputStyles} onChange={handleChange} />
      <Button label={"Submit"} onClick={handlePromptSubmit} clickable={inputText.length > 0}></Button>
    </div >
  )
}


export default Prompt
