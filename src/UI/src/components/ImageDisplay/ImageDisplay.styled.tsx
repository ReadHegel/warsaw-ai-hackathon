import { Stack } from "@mui/material";
import styled from "styled-components";

export const ImageDisplayWrapper = styled(Stack)`
    flex: 1;
    min-width: calc(30vw - 20px);
    padding: 10px;
    border-radius: 10px;
    align-items: center;
`;

export const ImageDisplayImg = styled.img`
    width: auto;

    max-width: calc(25vw - 20px);
    padding: 10px;
    border-radius: 10px;
    height: auto;
`;