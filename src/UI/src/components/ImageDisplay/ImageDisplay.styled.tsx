import { Box, Stack } from "@mui/material";
import styled from "styled-components";

export const ImageDisplayWrapper = styled(Stack)`
    flex: 1;
    min-width: calc(30vw - 20px);
    height: calc(90vh - 50px);
    padding: 10px;
    padding-top: 40px;
    justify-content: space-between;
    align-items: center;
`;

export const ImageDisplayImg = styled.img`
    grid-area: 1/1;
    width: 100%;
    height: auto;
    max-height: calc(70vh - 20px);
`;

export const ImageWrapper = styled(Stack)<{image: any}>`
    flex: 1;
    min-width: calc(30vw - 20px);
    max-height: calc(70vh - 20px);
    padding: 10px;
    align-items: center;
    display: grid;
    background-image: url(${(props) => props.image});
    background-size: contain;
    background-repeat: no-repeat;
    overflow: hidden;
`;

export const ImageControlsWrapper = styled(Box)`
    width: calc(100% - 20px);
    padding: 10px;
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 8px;
    overflow: hidden;
`;