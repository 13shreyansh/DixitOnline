import { useState } from "react"
import "./playerList.css"
import Button from "../../components/button.jsx";
import socket from "../../socketConfig.jsx";

function PlayerList(props) {

    let items = []
    for (let player in props.names) {
        items.push(<li key={player}>{props.names[player]}</li>)
    }

    function handleStartGame(){
      socket.emit("start_game", {});
    }

    return (
        <div id="container">
            <h2>Players:</h2>
            <div id="playerlist" className="info_text">
                <ul>
                    { items }
                </ul>
            </div>
          <Button label={"Start Prompt Match"} onClick={handleStartGame}></Button>
        </div>
    )
}

export default PlayerList
