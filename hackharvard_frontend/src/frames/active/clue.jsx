import "src/App.css"
import "./clue.css"

import Button from "src/components/button.jsx"
import socket from "../../socketConfig.jsx";
import {backend_url} from "../../backendUrl.jsx";

function ActivePlayerClue(props) {

    var inputStyles = {
        "width": "100%",
        "height": "30px",
        "fontSize": "30px",
        // "border": "none",
        // "outline": "none"
    };

    function handleAPCDone() {
      socket.emit("active_player_proceed", {})
        console.log('Done');
    }

    return (
        <div id="clue_container">
            <div id="apc_info" className="info_text">
                {"Your image is ready."}
                <br />
                {"Move to the next step when everyone has seen the TV."}
            </div>
           <div className={"card_image"}>
             <img src={backend_url + props.info.image} alt="Generated card" />
           </div>
            <Button label="Done" onClick={handleAPCDone} />
        </div >
    )
}

export default ActivePlayerClue
