import { Box, Stack, Typography } from "@mui/material";
import styled from "styled-components";

export const ChatWrapper = styled(Stack)`
    width: calc(100% - 20px);
    min-height: calc(90vh - 20px);
    height: fit-content;
    padding: 10px;
    display: flex;
    gap: 2;
    padding: 2;
    flex-direction: row;
`;

export const ConversationsContainer = styled(Stack)`
    margin-left: auto;
    margin-right: auto;
`;

export const ConvWrapper = styled(Stack).attrs({direction: 'row', gap: 2})`
    width: calc(40vw - 20px);
    padding: 10px;
    justify-content: space-between;
    background: rgba(255,255,255,.2);
    border-radius: 10px;
    cursor: pointer;
    color: inherit !important;

    &:hover {
        filter: brightness(110%);
    }
`;

export const ConvIndexTypography = styled(Typography)`
    padding-left: 30px;
    padding-right: 20px;
`;

export const ConvTypography = styled(Typography)`
    flex: 1;
    padding-left: 40px;
`;