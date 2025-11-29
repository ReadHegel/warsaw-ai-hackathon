import { useEffect, useState } from "react";
import { ChatWrapper, ConversationsContainer, ConvIndexTypography, ConvTypography, ConvWrapper } from "./ChatsHistory.styled"
import axios from "axios";
import { Link, Stack, Typography } from "@mui/material";

type ChatRow = {
    id: number;
    name: string;
}

export const ChatsHistory = () => {

    const [convs, setConvs] = useState<ChatRow[]>([]);

    const getAllConvs = async() => {
        try {
            const res = await axios.get('/localApi/getConvs');
            console.log(res);
            setConvs(res.data);
        } catch (error){
            console.log(error);
        }
    }

    useEffect(() => {
        getAllConvs();
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
            {
                convs.length === 0 ? 
                <Typography variant='h3'>
                    No conversations found
                </Typography> : (<ConversationsContainer gap={1}>
                    {
                        convs.map((elem) => <Link href={`/chat/${elem.id}-${elem.name}`}
                            key={`${elem.id}-${elem.name}`}
                            underline="none">
                                <ConvWrapper>
                            <ConvIndexTypography variant="body1" color="inherit">
                                {elem.id}
                            </ConvIndexTypography>
                            <ConvTypography variant="body1" color="inherit">
                                {elem.name}
                            </ConvTypography>
                        </ConvWrapper>
                        </Link>)
                    }
                </ConversationsContainer>)
            }
        </ChatWrapper>
    )
}