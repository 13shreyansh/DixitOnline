import './App.css'
import socket from './socketConfig'

import RoleSelect from 'src/frames/roleSelect.jsx'
import WaitingScreen from 'src/frames/wait.jsx'
import PlayerResults from 'src/frames/playerResults'
import Prompt from 'src/frames/prompt.jsx';

import { useEffect, useState } from 'react'
import BotVote from './frames/bot/vote'
import Vote from './frames/tv/vote.jsx'
import PlayerList from "./frames/tv/playerList.jsx";
import TvResults from "./frames/tv/resultsTv.jsx";
import Target from "./frames/tv/target.jsx";

function App() {
  const [gameState, setGameState] = useState("role_select");
  const [frameInfo, setFrameInfo] = useState({});

  useEffect(() => {
    socket.on("display_waiting_screen", (msg) => {
      console.log("Display waiting")
      setGameState("wait");
      setFrameInfo(msg);
    });

    socket.on("display_vote", (msg) => {
      console.log("Display vote")
      setGameState("bot_vote");
      setFrameInfo(msg);
    })

    socket.on("display_prompt", (msg) => {
      console.log("Display prompt")
      setGameState("prompt");
      setFrameInfo(msg);
    })

    socket.on("player_display_results", (msg) => {
      console.log("Display player results")
      setGameState("player_results");
      setFrameInfo(msg);
    })

    socket.on("tv_show_player_list", (msg) => {
      console.log("Tv show player list");
      setGameState("lobby");
      setFrameInfo(msg);
    })

    socket.on("tv_show_cards_vote", (msg) => {
      console.log("Tv show cards vote");
      setGameState("tv_vote");
      setFrameInfo(msg);
    });

    socket.on("tv_show_target", (msg) => {
      console.log("Tv show target");
      setGameState("tv_target");
      setFrameInfo(msg);
    });

    socket.on("tv_display_results", (msg) => {
      console.log("Tv display results");
      setGameState("tv_results");
      setFrameInfo(msg);
    })
  }, []);


  // ajsdkjalskdjalksjdlakjsdlkajsdlkjaslkdjaslkdjalskdjalksdjaslkdjalskdjalskdjalskdjaslkdj

  if (gameState == "role_select") {
    return (
      <div id="app_frame">
        <RoleSelect info={frameInfo} />
      </div>
    )
  }

  if (gameState == "wait") {
    return (
      <div id="app_frame">
        <WaitingScreen info={frameInfo} />
      </div>
    )
  }

  if (gameState == "bot_vote") {
    return (
      <div id="app_frame">
        <BotVote info={frameInfo} />
      </div>
    )
  }

  if (gameState == "prompt") {
    return (
      <div id="app_frame">
        <Prompt info={frameInfo} />
      </div>
    )
  }

  if (gameState == "player_results") {
    return (
      <div id="app_frame">
        <PlayerResults info={frameInfo} />
      </div>
    )
  }

  let screen = [];
  if(gameState === "lobby"){
    screen.push(<PlayerList key={"playerlist"} names={frameInfo.names}></PlayerList>)
  } else if(gameState === "tv_target"){
    screen.push(<Target key={"target"} info={frameInfo}></Target>)
  } else if(gameState === "tv_vote"){
    screen.push(<Vote key={"vote"} target_image={frameInfo.target_image} images={frameInfo.images}></Vote>)
  } else if(gameState === "tv_results"){
    screen.push(<TvResults target_image={frameInfo.target_image} target_prompt={frameInfo.target_prompt} images={frameInfo.images} players={frameInfo.players}></TvResults>)
  }

  return (
    <div id="app_frame">
      {screen}
    </div>
  )


}

export default App
