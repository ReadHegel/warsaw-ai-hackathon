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
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Message = {
    role: 'user' | 'assistant',
    content: string
}

export const Chat = () => {

    const [chat, setChat] = useState<Message[]>([]);

    const [mess, setMess] = useState('');
    const [chatSize, setChatSize] = useState<1|3>(3);
    const [status, setStatus] = useState<"loading" | "idle">("idle");
    const [chatId, setChatId] = useState<string|null>(null);
    const [imageUrl, setImageUrl] = useState<string>('');
    const [imageBlob, setImageBlob] = useState<BlobPart | null>(null);
    const [maskUrl, setMaskUrl] = useState<string>('');
    const [error, setError] = useState(false);

    const params = useParams();

    const sendMessage = async() => {
        setError(false);
        setStatus("loading");
        const userMess = mess;
        const newHistory = [...chat, {
            role: "user",
            content: userMess
        }];
        setChat((curr) => [...curr, {
            role: "user",
            content: userMess
        }]);
        setMess('');
        try {
            const file = new File([imageBlob as BlobPart], "image.png", { type: "image/png" });
            const formData = new FormData();
            formData.append("chat_history", JSON.stringify(newHistory));
            formData.append("image", file);
            const res = await axios.post('http://localhost:8899/segment_image', formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );

            const {chat_response, masked_image_path} = res.data;
            console.log('jest kurwa', res);
            await getImage(masked_image_path, setMaskUrl); 
            setStatus("idle");
            setChat((curr) => [...curr, {
                role: "assistant",
                content: chat_response
            }]);

            let baseId = chatId;
            if(chatId === null){
                const res = await axios.post('/localApi/createNewConv');
                const newChatId = res.data.newId.replaceAll("\"", '');
                console.log(newChatId);
                setChatId(newChatId); 
                baseId = newChatId;
            }
            const saveData = await axios.post('/localApi/saveConvToDb', {
                assistantMess: chat_response,
                userMess,
                baseId
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            window.history.pushState({}, "", `/chat/${baseId}`);
        } catch (error){
            setError(true);
            console.log(error);
        }
        
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

    const getImage = async(path="Images/geoportal_ortho_r1_c1.png", urlHandler=setImageUrl) => {
        try {
            const res = await fetch(`http://localhost:8899/image?path=${path}`).then(res => res.blob())
            .then(blob => {
                if(urlHandler === setImageUrl){
                    setImageBlob(blob);
                }
                const url = URL.createObjectURL(blob);
                urlHandler(url);
            });;
        } catch (err) {
            console.log(err);
        }
    }

    useEffect(() => {
        const buffer:HTMLElement|null = document.getElementById("printBuffer");
        if(buffer !== null) buffer.scrollTop = buffer?.scrollHeight;
    }, [chat, status]);

    useEffect(() => {
        console.log(params.chatId);
        if(params.chatId && params.chatId.split('-').length === 2){
            setChatId(params.chatId);
            loadConversation(params.chatId);
        }
    }, [params]);

    useEffect(() => {
        getImage();
    }, []);

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
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {mess.content}
                                </ReactMarkdown>
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
            <ImageDisplay 
                showControls={chatSize === 1} 
                url={imageUrl}
                maskUrl={maskUrl}
            />
        </ChatWrapper>
    )
}