import "src/App.css"
import Button from "../../components/button.jsx";
import socket from "../../socketConfig.jsx";

function BotVote(props) {
  let vote_buttons = []

  function voteFor(num){
    socket.emit("vote", {"vote": num})
  }

  let options = props.info.options || Array.from({length: props.info.number}, (_, index) => ({index}));
  for(let option of options){
    vote_buttons.push(
        <Button id="votes" key={option.index} label={option.index + 1} onClick={()=>voteFor(option.index)} clickable={true}></Button>
    )
  }
    return (
        <div id="vote_container">
          <div id="wait_info">
            Vote for the closest match on the TV. The images are anonymous.
          </div>
          <div id="vote_button_container">
            {vote_buttons}
          </div>
        </div>
    )
}

export default BotVote
