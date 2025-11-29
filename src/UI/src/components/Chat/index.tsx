import { useEffect, useState } from "react"
import { ImageDisplay } from "../ImageDisplay"
import { 
    ChatAssistantMessage, 
    ChatMessagesSection, 
    ChatSectionContainer, 
    ChatUserInput, 
    ChatUserInputButton, 
    ChatUserInputWrapper, 
    ChatUserMessage, 
    ChatWrapper 
} from "./Chat.styled"
import { Typography } from "@mui/material"
import SendIcon from '@mui/icons-material/Send';
import { ImageHiding } from "../ImageHiding";
import { useParams } from "react-router";
import axios from "axios";

type Message = {
    role: 'user' | 'assistant',
    content: string
}

export const Chat = () => {

    const [chat, setChat] = useState<Message[]>([]);

    const [mess, setMess] = useState('');
    const [chatSize, setChatSize] = useState<1|3>(1);
    const [status, setStatus] = useState<"loading" | "idle">("idle");

    const params = useParams();

    const sendMessage = async() => {
        setStatus("loading");
        setChat((curr) => [...curr, {
            role: "user",
            content: mess
        }]);
        setMess('');
        const {content} = await new Promise<{content: string}>((res) => {
            setTimeout(() => {
                return res({
                    content: "Hello There!"
                })
            }, 2000)
        })
        setStatus("idle");
        setChat((curr) => [...curr, {
            role: "assistant",
            content
        }]);
    }

    const loadConversation = async(baseId: string) => {
        try {
            const res = await axios.get(`/localApi/getConv/${baseId}`);
            const data = res.data as {id: number, sender: 'user' | 'assistant', content: string}[];
            setChat(data.map((elem) => ({role: elem.sender, content: elem.content})));
        } catch (error){
            console.error(error);
        }
    }

    const triggerLayoutShift = () => {
        setChatSize((curr) => curr === 3 ? 1 : 3);
    }

    useEffect(() => {
        const buffer:HTMLElement|null = document.getElementById("printBuffer");
        if(buffer !== null) buffer.scrollTop = buffer?.scrollHeight;
    }, [chat, status]);

    useEffect(() => {
        console.log(params.chatId);
        if(params.chatId && params.chatId.split('-').length === 2){
            loadConversation(params.chatId);
        }
    }, [params]);

    return (
        <ChatWrapper sx={(theme) => ({
            backgroundColor: theme.palette.background.default,
            display: "flex",
            flexDirection: "row",
            gap: 2,
            padding: 2,
            minHeight: '96vh'
        })}
        >
            <ChatSectionContainer style={{
                flex: chatSize
            }}>
                <ChatMessagesSection id="printBuffer">
                    {
                        chat.length === 0 ?
                            <Typography variant="h3" align="center" sx={{
                                color: "white"
                            }}>
                                Start your conversation!
                            </Typography>
                        : chat.map((mess, ind) => mess.role === 'user' ? (
                            <ChatUserMessage key={`mess-${ind}`}>
                                <Typography variant='body1'>
                                    {mess.content}
                                </Typography>
                            </ChatUserMessage>
                        ) : (
                            <ChatAssistantMessage key={`mess-${ind}`}>
                                <Typography variant='body1'>
                                    {mess.content}
                                </Typography>
                            </ChatAssistantMessage>
                        ))
                    }
                    {status === "loading" && <div className="loader"/>}
                </ChatMessagesSection>
                <ChatUserInputWrapper direction='row'>
                    <ChatUserInput 
                        type="text" 
                        placeholder="Enter your prompt..." 
                        value={mess}
                        onChange={(e) => setMess(e.currentTarget.value)}
                        onKeyDown={(key) => key.key === "Enter" && sendMessage()}
                    />
                    <ChatUserInputButton 
                        onClick={sendMessage} 
                        variant="outlined"
                        endIcon={<SendIcon />}
                        disabled={status === "loading"}
                    >
                        Send
                    </ChatUserInputButton>
                </ChatUserInputWrapper>
            </ChatSectionContainer>
            <ImageHiding onTrigger={triggerLayoutShift}/>
            <ImageDisplay showControls={chatSize === 1} />
        </ChatWrapper>
    )
}