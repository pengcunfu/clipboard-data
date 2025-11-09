import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import { listen } from "@tauri-apps/api/event";
import { writeText, readText } from "@tauri-apps/api/clipboard";
import { save } from "@tauri-apps/api/dialog";
import {
  Layout,
  List,
  Button,
  Input,
  Typography,
  Space,
  Switch,
  message,
  Modal,
  Card,
  Tag,
} from "antd";
import {
  DeleteOutlined,
  CopyOutlined,
  ExportOutlined,
  SearchOutlined,
  AudioOutlined,
  AudioMutedOutlined,
} from "@ant-design/icons";

const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Title, Text } = Typography;

interface ClipboardEntry {
  timestamp: string;
  text: string;
}

function App() {
  const [history, setHistory] = useState<ClipboardEntry[]>([]);
  const [filteredHistory, setFilteredHistory] = useState<ClipboardEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<ClipboardEntry | null>(null);
  const [monitoring, setMonitoring] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [lastClipboard, setLastClipboard] = useState("");

  // Load history on mount
  useEffect(() => {
    loadHistory();
    loadMonitoringStatus();

    // Listen for monitoring changes from system tray
    const unlisten = listen("monitoring-changed", (event) => {
      setMonitoring(event.payload as boolean);
    });

    return () => {
      unlisten.then((fn) => fn());
    };
  }, []);

  // Monitor clipboard changes
  useEffect(() => {
    if (!monitoring) return;

    const interval = setInterval(async () => {
      try {
        const text = await readText();
        if (text && text.trim() && text !== lastClipboard) {
          setLastClipboard(text);
          const entry = await invoke<ClipboardEntry>("add_to_history", { text });
          setHistory((prev) => [entry, ...prev]);
          setFilteredHistory((prev) => [entry, ...prev]);
        }
      } catch (error) {
        console.error("Failed to read clipboard:", error);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [monitoring, lastClipboard]);

  // Filter history based on search
  useEffect(() => {
    if (!searchText) {
      setFilteredHistory(history);
    } else {
      const filtered = history.filter(
        (entry) =>
          entry.text.toLowerCase().includes(searchText.toLowerCase()) ||
          entry.timestamp.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredHistory(filtered);
    }
  }, [searchText, history]);

  const loadHistory = async () => {
    try {
      const hist = await invoke<ClipboardEntry[]>("get_history");
      setHistory(hist);
      setFilteredHistory(hist);
      if (hist.length > 0) {
        setSelectedEntry(hist[0]);
      }
    } catch (error) {
      message.error("加载历史记录失败");
      console.error(error);
    }
  };

  const loadMonitoringStatus = async () => {
    try {
      const status = await invoke<boolean>("get_monitoring_status");
      setMonitoring(status);
    } catch (error) {
      console.error(error);
    }
  };

  const handleToggleMonitoring = async () => {
    try {
      const newStatus = await invoke<boolean>("toggle_monitoring");
      setMonitoring(newStatus);
      message.success(newStatus ? "监听已开启" : "监听已关闭");
    } catch (error) {
      message.error("切换监听状态失败");
      console.error(error);
    }
  };

  const handleClear = () => {
    Modal.confirm({
      title: "确认清空",
      content: "确定要清空所有历史记录吗？此操作不可恢复！",
      okText: "确定",
      cancelText: "取消",
      onOk: async () => {
        try {
          await invoke("clear_history");
          setHistory([]);
          setFilteredHistory([]);
          setSelectedEntry(null);
          message.success("历史记录已清空");
        } catch (error) {
          message.error("清空历史记录失败");
          console.error(error);
        }
      },
    });
  };

  const handleCopy = async () => {
    if (!selectedEntry) {
      message.warning("请先选择一条记录");
      return;
    }
    try {
      await writeText(selectedEntry.text);
      message.success("已复制到剪贴板");
    } catch (error) {
      message.error("复制失败");
      console.error(error);
    }
  };

  const handleExport = async () => {
    try {
      const filePath = await save({
        defaultPath: "clipboard_history.txt",
        filters: [{ name: "Text Files", extensions: ["txt"] }],
      });

      if (filePath) {
        await invoke("export_history", { filePath });
        message.success("导出成功");
      }
    } catch (error) {
      message.error("导出失败");
      console.error(error);
    }
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  return (
    <div className="container">
      <Layout style={{ height: "100vh" }}>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          <Title level={3} style={{ margin: 0 }}>
            剪贴板自动收集工具
          </Title>
          <Space>
            <Text>监听状态:</Text>
            <Switch
              checked={monitoring}
              onChange={handleToggleMonitoring}
              checkedChildren={<AudioOutlined />}
              unCheckedChildren={<AudioMutedOutlined />}
            />
            <Tag color={monitoring ? "success" : "default"}>
              {monitoring ? "正在监听" : "未监听"}
            </Tag>
          </Space>
        </Header>

        <Layout>
          <Sider
            width={450}
            style={{
              background: "#fff",
              borderRight: "1px solid #f0f0f0",
              padding: "16px",
            }}
          >
            <Space direction="vertical" style={{ width: "100%" }} size="middle">
              <Input
                placeholder="搜索历史记录..."
                prefix={<SearchOutlined />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
              />

              <div style={{ height: "calc(100vh - 240px)", overflowY: "auto" }}>
                <List
                  dataSource={filteredHistory}
                  renderItem={(item) => (
                    <List.Item
                      onClick={() => setSelectedEntry(item)}
                      style={{
                        cursor: "pointer",
                        background:
                          selectedEntry?.timestamp === item.timestamp
                            ? "#e6f7ff"
                            : "#fafafa",
                        marginBottom: 8,
                        padding: 12,
                        borderRadius: 4,
                        border:
                          selectedEntry?.timestamp === item.timestamp
                            ? "1px solid #1890ff"
                            : "1px solid #f0f0f0",
                      }}
                    >
                      <List.Item.Meta
                        title={
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {item.timestamp}
                          </Text>
                        }
                        description={
                          <Text ellipsis style={{ fontSize: 14 }}>
                            {truncateText(item.text.replace(/\n/g, " "))}
                          </Text>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>

              <Space style={{ width: "100%", justifyContent: "space-between" }}>
                <Button
                  type="primary"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={handleClear}
                >
                  清空
                </Button>
                <Button icon={<CopyOutlined />} onClick={handleCopy}>
                  复制
                </Button>
                <Button icon={<ExportOutlined />} onClick={handleExport}>
                  导出
                </Button>
              </Space>
            </Space>
          </Sider>

          <Content style={{ padding: "16px", background: "#f5f5f5" }}>
            <Card
              title="内容预览"
              style={{ height: "100%" }}
              bodyStyle={{ height: "calc(100% - 57px)" }}
            >
              <TextArea
                value={selectedEntry?.text || ""}
                readOnly
                style={{
                  height: "100%",
                  fontFamily: "Microsoft YaHei, monospace",
                  fontSize: 14,
                }}
                placeholder="选择一条记录查看详细内容"
              />
            </Card>
          </Content>
        </Layout>
      </Layout>
    </div>
  );
}

export default App;
