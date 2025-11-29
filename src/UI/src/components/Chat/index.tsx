import { useEffect, useRef, useState } from "react"
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

type Message = {
    role: 'user' | 'assistant',
    content: string
}

export const Chat = () => {

    const bottomRef = useRef<HTMLDivElement | null>(null);

    const [chat, setChat] = useState<Message[]>([{
        role: "user",
        content: "Lorem ipsum dolor sit amet"
    },{
        role: "assistant",
        content: "Lorem ipsum dolor sit amet is the answer"
    },]);

    const [mess, setMess] = useState('');
    const [chatSize, setChatSize] = useState<1|3>(1);
    const [status, setStatus] = useState<"loading" | "idle">("idle");

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

    const triggerLayoutShift = () => {
        setChatSize((curr) => curr === 3 ? 1 : 3);
    }

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chat, status]);

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
                <ChatMessagesSection>
                    {
                        chat.map((mess, ind) => mess.role === 'user' ? (
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
                    <div ref={bottomRef} />
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