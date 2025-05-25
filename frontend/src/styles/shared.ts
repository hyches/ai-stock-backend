import { Theme } from '@mui/material/styles';

export const sharedStyles = {
  paper: {
    p: 2,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  tableContainer: {
    maxHeight: 440,
  },
  chartContainer: {
    height: 400,
    width: '100%',
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '80vh',
  },
  errorContainer: {
    p: 3,
  },
  header: {
    mb: 2,
  },
  gridContainer: {
    spacing: 3,
  },
  card: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  cardContent: {
    flexGrow: 1,
  },
  chip: {
    ml: 1,
  },
  tooltip: {
    maxWidth: 300,
  },
  button: {
    mt: 2,
  },
  form: {
    width: '100%',
    mt: 1,
  },
  formControl: {
    minWidth: 120,
  },
  select: {
    width: '100%',
  },
  textField: {
    width: '100%',
  },
  dialog: {
    minWidth: 400,
  },
  dialogContent: {
    minHeight: 200,
  },
  dialogActions: {
    p: 2,
  },
  alert: {
    mb: 2,
  },
  divider: {
    my: 2,
  },
  list: {
    width: '100%',
  },
  listItem: {
    py: 1,
  },
  listItemText: {
    primary: {
      fontWeight: 'bold',
    },
  },
  badge: {
    mr: 2,
  },
  avatar: {
    bgcolor: 'primary.main',
  },
  menu: {
    mt: 1,
  },
  menuItem: {
    px: 2,
  },
  toolbar: {
    justifyContent: 'space-between',
  },
  appBar: {
    zIndex: (theme: Theme) => theme.zIndex.drawer + 1,
  },
  drawer: {
    width: 240,
    flexShrink: 0,
  },
  drawerPaper: {
    width: 240,
  },
  drawerContainer: {
    overflow: 'auto',
  },
  content: {
    flexGrow: 1,
    p: 3,
  },
  footer: {
    py: 3,
    px: 2,
    mt: 'auto',
    backgroundColor: (theme: Theme) =>
      theme.palette.mode === 'light'
        ? theme.palette.grey[200]
        : theme.palette.grey[800],
  },
}; 