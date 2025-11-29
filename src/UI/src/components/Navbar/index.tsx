import { AppBar, Button, Toolbar, Typography } from "@mui/material"

export const Navbar = () => {
    return (<AppBar position="static">
        <Toolbar sx={{gap: 2}}>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Wiesio.AI
            </Typography>
            <Button color="inherit" href="/">
                New chat
            </Button>
            <Button color="inherit" href="/chats">
                Your chats
            </Button>
        </Toolbar>
    </AppBar>);
}