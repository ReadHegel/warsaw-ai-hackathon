import { Button, Input, Paper, Stack } from "@mui/material";
import styled from "styled-components";

export const ChatWrapper = styled(Stack)`
    width: calc(100% - 20px);
    max-height: calc(90vh - 20px);
    overflow-y: hidden;
    padding: 10px;
    display: flex;
    gap: 2;
    padding: 2;
    flex-direction: row;
`;

export const ChatSectionContainer = styled(Stack)`
    max-height: calc(90vh - 20px);
    padding: 10px;
    border-radius: 10px;
    transition: flex 0.2s;
`;

export const ChatMessagesSection = styled(Stack)`
    flex: 1;
    overflow-y: scroll;
    gap: 16px;
    padding-bottom: 20px;
    overscroll-behavior: contain;
`;

export const ChatUserMessage = styled(Paper)`
    width: calc(60% - 30px);
    padding: 15px;
    border-radius: 10px;
    text-align: left;
    background: red;
    display: block;
    margin-left: auto;
`;

export const ChatAssistantMessage = styled(Paper)`
    width: calc(60% - 30px);
    padding: 15px;
    border-radius: 10px;
    text-align: left;
    background: red;
    float: left;
`;

export const ChatUserInputWrapper = styled(Stack)`
    gap: 8px;
`;

export const ChatUserInput = styled(Input)`
    flex: 1;
    padding: 10px;
`;

export const ChatUserInputButton = styled(Button)`
    padding: 10px 30px;
    border-radius: 10px;
`;