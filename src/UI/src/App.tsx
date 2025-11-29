import { ThemeProvider } from "@mui/material";
import { Chat } from "./components/Chat";
import "./index.css";
import { createTheme } from "@mui/material/styles";
import { Navbar } from "./components/Navbar";
import { createBrowserRouter, RouterProvider } from "react-router";
import { ChatsHistory } from "./components/ChatsHistory";

export const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

const router = createBrowserRouter([{
  path: '/',
  element: <>
    <Navbar/>
    <Chat />
  </>,
}, {
  path: 'chats',
  element: <>
    <Navbar/>
    <ChatsHistory />
  </>,
}, {
  path: '/chat/:chatId',
  element: <>
    <Navbar/>
    <Chat />
  </>
}])

export function App() {
  return (
      <ThemeProvider theme={darkTheme}>
        <RouterProvider router={router}/>
      </ThemeProvider>
  );
}

export default App;
